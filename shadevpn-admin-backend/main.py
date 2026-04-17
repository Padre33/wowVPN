from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
import os, json, base64, secrets, asyncio, logging, uuid
from datetime import datetime, timedelta


try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logging.warning("[WARN] psutil not installed — system metrics will be unavailable. Run: pip install psutil")

from database import (
    SessionLocal, ClientDB, GroupDB, TemplateDB, NodeDB, RuleDB, SettingsDB, TrafficSnapshotDB
)
from sync import generate_key_and_add_to_json, read_clients_db, write_clients_db


# ═══════════════════  Background Traffic Collector  ═══════════════════

LAST_TRAFFIC_STATE = {}
LIVE_CLIENT_STATUS = {}
LIVE_CLIENT_TRAFFIC = {}

import subprocess, re

def parse_bytes(s):
    s = s.strip()
    if not s or s == "0 B": return 0.0
    try:
        val, unit = s.split(" ")
        val = float(val)
        if unit == "KB": return val * 1024
        if unit == "MB": return val * 1024**2
        if unit == "GB": return val * 1024**3
        if unit == "TB": return val * 1024**4
        return val
    except:
        return 0.0

async def traffic_collector():
    """Каждые 10 секунд читает live статистику из ОЗУ ядра и копит трафик"""
    while True:
        try:
            cmd = ["/opt/shadevpn/target/release/aivpn-server", "--list-clients", "--clients-db", "/etc/shadevpn/clients.json"]
            out = subprocess.check_output(cmd).decode("utf-8")
            lines = out.strip().splitlines()[2:]
            
            db = SessionLocal()
            for line in lines:
                if not line.strip() or line.startswith("Total:"): continue
                
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 7:
                    cid = parts[0]
                    last_seen_str = parts[-1].strip()
                    upload_str = parts[4]
                    download_str = parts[5]
                    
                    is_online = False
                    if last_seen_str and last_seen_str != "never":
                        try:
                            dt = datetime.strptime(last_seen_str, "%Y-%m-%d %H:%M")
                            if (datetime.utcnow() - dt).total_seconds() <= 300:
                                is_online = True
                        except Exception as e:
                            logging.error(f"Time parse error: {e}")
                    
                    bi = parse_bytes(download_str)
                    bo = parse_bytes(upload_str)

                    # Дельта-трекинг: если клиент видится впервые, стартовая точка = текущие значения (delta=0)
                    prev = LAST_TRAFFIC_STATE.get(cid, {"in": bi, "out": bo})
                    delta_in = bi - prev["in"]
                    delta_out = bo - prev["out"]
                    
                    if (delta_in + delta_out) > 0:
                        is_online = True

                    LIVE_CLIENT_STATUS[cid] = is_online
                    
                    # Если счетчик меньше предыдущего (VPN ядро перезапустилось)
                    if delta_in < 0: delta_in = bi
                    if delta_out < 0: delta_out = bo
                    
                    LAST_TRAFFIC_STATE[cid] = {"in": bi, "out": bo}
                    
                    total_delta_gb = (delta_in + delta_out) / (1024**3)
                    
                    if total_delta_gb > 0:
                        c = db.query(ClientDB).filter_by(id=cid).first()
                        if c:
                            c.data_usage += total_delta_gb
                            LIVE_CLIENT_TRAFFIC[cid] = c.data_usage
                            
                            now = datetime.utcnow()
                            snap = TrafficSnapshotDB(
                                client_id=c.id, timestamp=now,
                                bytes_in=delta_in, bytes_out=delta_out
                            )
                            db.add(snap)
            db.commit()
            db.close()
        except Exception as e:
            logging.error(f"Live collector warn: {e}")
            
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(traffic_collector())
    yield
    task.cancel()


app = FastAPI(title="ShadeVPN Admin Panel API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

ADMIN_PASSWORD = "admin" # Простой пароль по умолчанию

@app.middleware("http")
async def verify_admin(request: Request, call_next):
    if request.url.path.startswith("/api/login") or request.url.path.startswith("/api/sub/") or request.method == "OPTIONS":
        return await call_next(request)
    if not request.url.path.startswith("/api"):
        return await call_next(request)
        
    token = request.headers.get("X-Admin-Token")
    if token != ADMIN_PASSWORD:
        from starlette.responses import JSONResponse
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    return await call_next(request)

class LoginRequest(BaseModel):
    password: str

@app.post("/api/login")
def login(req: LoginRequest):
    if req.password == ADMIN_PASSWORD:
        return {"status": "ok"}
    from fastapi import HTTPException
    raise HTTPException(status_code=401, detail="Wrong password")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(SettingsDB).filter_by(key=key).first()
    return row.value if row else default

# ═══════════════════  Pydantic  ═══════════════════

class ClientCreate(BaseModel):
    username: str
    telegram_id: Optional[str] = None
    data_limit: float = 100.0
    group_id: Optional[str] = None
    subscription_days: Optional[int] = None

class ClientUpdate(BaseModel):
    username: Optional[str] = None
    telegram_id: Optional[str] = None
    data_limit: Optional[float] = None
    group_id: Optional[str] = None
    subscription_end: Optional[str] = None

class ClientToggle(BaseModel):
    enabled: bool

class GroupCreate(BaseModel):
    name: str
    description: str = ""
    data_limit: str = "100 ГБ/юзер"

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data_limit: Optional[str] = None

class TemplateCreate(BaseModel):
    name: str
    duration_days: int = 30
    data_limit_gb: float = 50.0
    price: str = "0"

class NodeCreate(BaseModel):
    name: str
    location: str = ""
    ip_address: str = ""
    port: int = 443

class RuleCreate(BaseModel):
    name: str
    trigger: str
    action: str
    enabled: bool = True

class RuleToggle(BaseModel):
    enabled: bool

class SettingsUpdate(BaseModel):
    settings: dict

class AssignGroup(BaseModel):
    client_ids: list[str]
    group_id: str


# ═══════════════════  Health  ═══════════════════

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ShadeVPN Admin API", "psutil": HAS_PSUTIL}


# ═══════════════════  System Metrics (psutil)  ═══════════════════

@app.get("/api/system")
def system_metrics():
    """Реальные метрики: CPU, RAM, диск, аптайм сервера"""
    if not HAS_PSUTIL:
        return {
            "cpu_percent": 0, "memory_total_gb": 0, "memory_used_gb": 0,
            "memory_percent": 0, "disk_total_gb": 0, "disk_used_gb": 0,
            "disk_free_gb": 0, "disk_percent": 0, "uptime_seconds": 0,
            "uptime_human": "psutil не установлен",
        }
    import time
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    boot = psutil.boot_time()
    uptime_s = int(time.time() - boot)
    days = uptime_s // 86400
    hours = (uptime_s % 86400) // 3600
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_total_gb": round(mem.total / (1024**3), 1),
        "memory_used_gb": round(mem.used / (1024**3), 1),
        "memory_percent": mem.percent,
        "disk_total_gb": round(disk.total / (1024**3), 0),
        "disk_used_gb": round(disk.used / (1024**3), 0),
        "disk_free_gb": round(disk.free / (1024**3), 0),
        "disk_percent": disk.percent,
        "uptime_seconds": uptime_s,
        "uptime_human": f"{days}d {hours}h",
    }


# ═══════════════════  Dashboard  ═══════════════════

@app.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    total = db.query(ClientDB).count()
    enabled = db.query(ClientDB).filter(ClientDB.enabled == True).count()
    disabled = total - enabled
    
    online = sum(1 for cid in LIVE_CLIENT_STATUS if LIVE_CLIENT_STATUS[cid])
    offline = total - online

    yesterday = datetime.utcnow() - timedelta(days=1)
    active_24h = db.query(TrafficSnapshotDB.client_id).filter(TrafficSnapshotDB.timestamp >= yesterday).distinct().count()

    ti = sum(snap.bytes_in for snap in db.query(TrafficSnapshotDB).all())
    to = sum(snap.bytes_out for snap in db.query(TrafficSnapshotDB).all())

    return {
        "totalClients": total,
        "enabledClients": enabled,
        "disabledClients": disabled,
        "onlineClients": online,
        "offlineClients": offline,
        "active24h": active_24h,
        "inactive24h": total - active_24h,
        "totalTrafficGB": round((ti + to) / (1024**3), 2),
        "downloadGB": round(ti / (1024**3), 2),
        "uploadGB": round(to / (1024**3), 2),
        "totalGroups": db.query(GroupDB).count(),
        "totalNodes": db.query(NodeDB).count(),
    }


# ═══════════════════  Traffic History  ═══════════════════

@app.get("/api/traffic/summary")
def traffic_summary(db: Session = Depends(get_db)):
    """Трафик за сегодня, 7 дней, 30 дней, месяц, год — реальный из снапшотов"""
    now = datetime.utcnow()

    def sum_period(since: datetime):
        row = db.query(
            sa_func.sum(TrafficSnapshotDB.bytes_in).label("bi"),
            sa_func.sum(TrafficSnapshotDB.bytes_out).label("bo"),
        ).filter(TrafficSnapshotDB.timestamp >= since).first()
        bi = row.bi or 0
        bo = row.bo or 0
        return round((bi + bo) / (1024**3), 2)

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    return {
        "todayGB": sum_period(today_start),
        "last7daysGB": sum_period(week_ago),
        "last30daysGB": sum_period(month_ago),
        "currentMonthGB": sum_period(month_start),
        "currentYearGB": sum_period(year_start),
    }


@app.get("/api/traffic/chart24h")
def traffic_chart_24h(db: Session = Depends(get_db)):
    """Почасовой трафик за последние 24 часа для графика"""
    now = datetime.utcnow()
    result = []
    for i in range(24):
        h_start = (now - timedelta(hours=23-i)).replace(minute=0, second=0, microsecond=0)
        h_end = h_start + timedelta(hours=1)
        row = db.query(
            sa_func.sum(TrafficSnapshotDB.bytes_in).label("bi"),
            sa_func.sum(TrafficSnapshotDB.bytes_out).label("bo"),
        ).filter(
            TrafficSnapshotDB.timestamp >= h_start,
            TrafficSnapshotDB.timestamp < h_end,
        ).first()
        bi = row.bi or 0
        bo = row.bo or 0
        gb = round((bi + bo) / (1024**3), 3)
        h_start_msk = h_start + timedelta(hours=3)
        result.append({"time": h_start_msk.strftime("%H:%M"), "traffic": gb})
    return result


# ═══════════════════  Clients  ═══════════════════

@app.get("/api/clients")
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(ClientDB).all()
    result = []
    
    for c in clients:
        group = db.query(GroupDB).filter_by(id=c.group_id).first() if c.group_id else None
        
        is_online = LIVE_CLIENT_STATUS.get(c.id, False)
        live_usage = LIVE_CLIENT_TRAFFIC.get(c.id, c.data_usage)

        # Build subscription link if sub_token exists
        if c.sub_token:
            server_ip = "185.204.52.135"
            sub_url = f"http://{server_ip}/api/sub/{c.sub_token}"
            sub_payload = json.dumps({"sub": sub_url}, separators=(',', ':'))
            sub_b64 = base64.urlsafe_b64encode(sub_payload.encode()).rstrip(b'=').decode()
            shade_link = f"shade://{sub_b64}"
        else:
            shade_link = c.psk

        result.append({
            "id": c.id, "username": c.name,
            "telegramId": c.telegram_id or "—",
            "protocol": c.protocol,
            "dataUsage": round(live_usage, 6), "dataLimit": c.data_limit,
            "subscriptionEnd": c.subscription_end.strftime("%Y-%m-%d") if c.subscription_end else "Безлимит",
            "status": "online" if c.enabled else "offline",
            "isOnline": is_online,
            "shadeLink": shade_link,
            "vpnIp": c.vpn_ip,
            "createdAt": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "",
            "groupName": group.name if group else "—",
            "groupId": c.group_id or "",
        })
    return result


@app.post("/api/clients")
def create_client(body: ClientCreate, db: Session = Depends(get_db)):
    if not body.username: raise HTTPException(400, "Username required")
    
    # 1. Use Rust Binary to generate mathematically correct keys and write to clients.json
    import subprocess
    cmd = [
        "/opt/shadevpn/target/release/aivpn-server",
        "--clients-db", "/etc/shadevpn/clients.json",
        "--key-file", "/etc/shadevpn/server.key",
        "--add-client", body.username,
        "--server-ip", "185.204.52.135"
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"Core generation failed: {e.output.decode('utf-8', 'ignore')}")
    
    # 2. Parse the output securely
    c_id = None
    link = None
    for line in out.splitlines():
        if line.strip().startswith("ID:"): c_id = line.split("ID:")[1].strip()
        if line.strip().startswith("shade://"): link = line.strip()
        
    if not c_id: raise HTTPException(500, "Could not parse client ID from Core")
    
    # 3. Read the newly injected IP from clients.json to sync DB
    from sync import read_clients_db
    core_db = read_clients_db()
    c_vpn_ip = "10.0.0.x"
    c_psk = ""
    for c in core_db.get("clients", []):
        if c.get("id") == c_id:
            c_vpn_ip = c.get("vpn_ip", "10.0.0.x")
            c_psk = c.get("psk", "")
            break
            
    # 4. Generate subscription token
    sub_token = str(uuid.uuid4())
    
    # 5. Build the subscription shade:// key
    server_ip = "185.204.52.135"
    sub_url = f"http://{server_ip}/api/sub/{sub_token}"
    sub_payload = json.dumps({"sub": sub_url}, separators=(',', ':'))
    sub_b64 = base64.urlsafe_b64encode(sub_payload.encode()).rstrip(b'=').decode()
    sub_shade_link = f"shade://{sub_b64}"
    
    # 6. Save to Panel DB
    new = ClientDB(
        id=c_id, name=body.username, psk=link, vpn_ip=c_vpn_ip,
        data_limit=body.data_limit, group_id=body.group_id,
        telegram_id=body.telegram_id, protocol="ShadeVPN",
        sub_token=sub_token
    )
    if body.subscription_days:
        new.subscription_end = datetime.utcnow() + timedelta(days=body.subscription_days)
    
    db.add(new)
    db.commit()
    
    # 7. Restart Core to hot-reload
    os.system("systemctl restart shadevpn")
    
    return {"status": "created", "shadeLink": sub_shade_link, "directLink": link, "subToken": sub_token}


@app.delete("/api/clients/{cid}")
def delete_client(cid: str, db: Session = Depends(get_db)):
    c = db.query(ClientDB).filter_by(id=cid).first()
    if not c: raise HTTPException(404, "Клиент не найден")
    db.delete(c)
    db.commit()
    
    from sync import read_clients_db, write_clients_db
    core = read_clients_db()
    core["clients"] = [x for x in core.get("clients", []) if x.get("id") != cid]
    write_clients_db(core)
    os.system("systemctl restart shadevpn")
    return {"status": "deleted"}

@app.patch("/api/clients/{cid}")
def update_client(cid: str, body: ClientUpdate, db: Session = Depends(get_db)):
    c = db.query(ClientDB).filter_by(id=cid).first()
    if not c: raise HTTPException(404, "Клиент не найден")
    
    needs_core_restart = False
    
    if body.username is not None and body.username != c.name:
        c.name = body.username
        
        # Обновляем имя в clients.json
        from sync import read_clients_db, write_clients_db
        core = read_clients_db()
        for cc in core.get("clients", []):
            if cc.get("id") == cid:
                cc["name"] = body.username
                needs_core_restart = True
        if needs_core_restart:
            write_clients_db(core)
            
    if body.telegram_id is not None:
        c.telegram_id = body.telegram_id
    if body.data_limit is not None:
        c.data_limit = body.data_limit
    if body.group_id is not None:
        c.group_id = body.group_id
    if body.subscription_end is not None:
        if body.subscription_end == "":
            c.subscription_end = None
        else:
            try:
                c.subscription_end = datetime.strptime(body.subscription_end, "%Y-%m-%d")
            except ValueError:
                pass
                
    db.commit()
    
    if needs_core_restart:
        os.system("systemctl restart shadevpn")
        
    return {"status": "updated"}

@app.get("/api/clients/{cid}/qr")
def get_client_qr(cid: str, db: Session = Depends(get_db)):
    """Backend endpoint to generate QR code dynamically without external scripts."""
    c = db.query(ClientDB).filter_by(id=cid).first()
    if not c or not c.psk or not c.psk.startswith("shade://"):
        raise HTTPException(404, "Ключ не найден для данного клиента")
    
    try:
        import qrcode
        import io
        from fastapi.responses import StreamingResponse
    except ImportError:
        raise HTTPException(500, "Библиотека qrcode не установлена (pip install qrcode[pil])")
    
    # Use subscription link if available
    if c.sub_token:
        server_ip = "185.204.52.135"
        sub_url = f"http://{server_ip}/api/sub/{c.sub_token}"
        sub_payload = json.dumps({"sub": sub_url}, separators=(',', ':'))
        sub_b64 = base64.urlsafe_b64encode(sub_payload.encode()).rstrip(b'=').decode()
        qr_content = f"shade://{sub_b64}"
    else:
        qr_content = c.psk
    
    img = qrcode.make(qr_content)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.patch("/api/clients/{cid}/toggle")
def toggle_client(cid: str, body: ClientToggle, db: Session = Depends(get_db)):
    c = db.query(ClientDB).filter_by(id=cid).first()
    if not c: raise HTTPException(404)
    c.enabled = body.enabled
    db.commit()
    core = read_clients_db()
    for cc in core.get("clients", []):
        if cc.get("id") == cid:
            cc["enabled"] = body.enabled
    write_clients_db(core)
    os.system("systemctl restart shadevpn")
    return {"status": "updated", "enabled": body.enabled}


# ═══════════════════  Groups  ═══════════════════

@app.get("/api/groups")
def list_groups(db: Session = Depends(get_db)):
    groups = db.query(GroupDB).all()
    result = []
    for g in groups:
        members = db.query(ClientDB).filter_by(group_id=g.id).count()
        result.append({
            "id": g.id, "name": g.name, "description": g.description,
            "dataLimit": g.data_limit, "members": members,
        })
    return result


@app.post("/api/groups")
def create_group(data: GroupCreate, db: Session = Depends(get_db)):
    gid = secrets.token_hex(4)
    g = GroupDB(id=gid, name=data.name, description=data.description, data_limit=data.data_limit)
    db.add(g); db.commit()
    return {"status": "created", "id": gid}


@app.patch("/api/groups/{gid}")
def update_group(gid: str, data: GroupUpdate, db: Session = Depends(get_db)):
    g = db.query(GroupDB).filter_by(id=gid).first()
    if not g: raise HTTPException(404)
    if data.name is not None: g.name = data.name
    if data.description is not None: g.description = data.description
    if data.data_limit is not None: g.data_limit = data.data_limit
    db.commit()
    return {"status": "updated"}


@app.delete("/api/groups/{gid}")
def delete_group(gid: str, db: Session = Depends(get_db)):
    g = db.query(GroupDB).filter_by(id=gid).first()
    if not g: raise HTTPException(404)
    for c in db.query(ClientDB).filter_by(group_id=gid).all():
        c.group_id = None
    db.delete(g); db.commit()
    return {"status": "deleted"}


@app.post("/api/groups/{gid}/assign")
def assign_clients_to_group(gid: str, body: AssignGroup, db: Session = Depends(get_db)):
    g = db.query(GroupDB).filter_by(id=gid).first()
    if not g: raise HTTPException(404)
    for cid in body.client_ids:
        c = db.query(ClientDB).filter_by(id=cid).first()
        if c: c.group_id = gid
    db.commit()
    return {"status": "assigned"}


# ═══════════════════  Templates  ═══════════════════

@app.get("/api/templates")
def list_templates(db: Session = Depends(get_db)):
    return [{
        "id": t.id, "name": t.name,
        "durationDays": t.duration_days,
        "dataLimitGb": t.data_limit_gb,
        "price": t.price,
    } for t in db.query(TemplateDB).all()]


@app.post("/api/templates")
def create_template(data: TemplateCreate, db: Session = Depends(get_db)):
    tid = secrets.token_hex(4)
    t = TemplateDB(id=tid, name=data.name, duration_days=data.duration_days,
                   data_limit_gb=data.data_limit_gb, price=data.price)
    db.add(t); db.commit()
    return {"status": "created", "id": tid}


@app.delete("/api/templates/{tid}")
def delete_template(tid: str, db: Session = Depends(get_db)):
    t = db.query(TemplateDB).filter_by(id=tid).first()
    if not t: raise HTTPException(404)
    db.delete(t); db.commit()
    return {"status": "deleted"}


# ═══════════════════  Nodes (Servers)  ═══════════════════

@app.get("/api/nodes")
def list_nodes(db: Session = Depends(get_db)):
    return [{
        "id": n.id, "name": n.name, "location": n.location,
        "ipAddress": n.ip_address, "port": n.port,
        "isOnline": n.is_online,
    } for n in db.query(NodeDB).all()]


@app.post("/api/nodes")
def create_node(data: NodeCreate, db: Session = Depends(get_db)):
    nid = secrets.token_hex(4)
    n = NodeDB(id=nid, name=data.name, location=data.location,
               ip_address=data.ip_address, port=data.port)
    db.add(n); db.commit()
    return {"status": "created", "id": nid}


@app.delete("/api/nodes/{nid}")
def delete_node(nid: str, db: Session = Depends(get_db)):
    n = db.query(NodeDB).filter_by(id=nid).first()
    if not n: raise HTTPException(404)
    db.delete(n); db.commit()
    return {"status": "deleted"}


# ═══════════════════  Subscription API (Public)  ═══════════════════

COUNTRY_FLAGS = {
    "NL": "🇳🇱", "NLD": "🇳🇱", "Netherlands": "🇳🇱", "Нидерланды": "🇳🇱",
    "TR": "🇹🇷", "TUR": "🇹🇷", "Turkey": "🇹🇷", "Турция": "🇹🇷",
    "DE": "🇩🇪", "DEU": "🇩🇪", "Germany": "🇩🇪", "Германия": "🇩🇪",
    "US": "🇺🇸", "USA": "🇺🇸", "United States": "🇺🇸", "США": "🇺🇸",
    "RU": "🇷🇺", "RUS": "🇷🇺", "Russia": "🇷🇺", "Россия": "🇷🇺",
    "GB": "🇬🇧", "GBR": "🇬🇧", "UK": "🇬🇧", "Великобритания": "🇬🇧",
    "FR": "🇫🇷", "FRA": "🇫🇷", "France": "🇫🇷", "Франция": "🇫🇷",
    "JP": "🇯🇵", "JPN": "🇯🇵", "Japan": "🇯🇵", "Япония": "🇯🇵",
    "ES": "🇪🇸", "ESP": "🇪🇸", "Spain": "🇪🇸", "Испания": "🇪🇸",
    "EE": "🇪🇪", "EST": "🇪🇪", "Estonia": "🇪🇪", "Эстония": "🇪🇪",
    "FI": "🇫🇮", "FIN": "🇫🇮", "Finland": "🇫🇮", "Финляндия": "🇫🇮",
    "SE": "🇸🇪", "SWE": "🇸🇪", "Sweden": "🇸🇪", "Швеция": "🇸🇪",
    "CA": "🇨🇦", "CAN": "🇨🇦", "Canada": "🇨🇦", "Канада": "🇨🇦",
    "SG": "🇸🇬", "SGP": "🇸🇬", "Singapore": "🇸🇬", "Сингапур": "🇸🇬",
    "IN": "🇮🇳", "IND": "🇮🇳", "India": "🇮🇳", "Индия": "🇮🇳",
}

def get_flag(location: str) -> str:
    """Get country flag emoji from location string"""
    import re
    # Match whole words to avoid 'es' matching 'estonia' or 'nl' matching 'finland'
    loc_lower = location.lower()
    for key, flag in COUNTRY_FLAGS.items():
        if re.search(r'\b' + re.escape(key.lower()) + r'\b', loc_lower):
            return flag
    return "🌐"

def get_country_code(location: str) -> str:
    """Extract 2-letter country code from location"""
    code_map = {
        "Netherlands": "NL", "Нидерланды": "NL", "NL": "NL",
        "Turkey": "TR", "Турция": "TR", "TR": "TR",
        "Germany": "DE", "Германия": "DE", "DE": "DE",
        "Russia": "RU", "Россия": "RU", "RU": "RU",
        "United States": "US", "США": "US", "US": "US",
        "France": "FR", "Франция": "FR", "FR": "FR",
        "UK": "GB", "Великобритания": "GB", "GB": "GB",
        "Japan": "JP", "Япония": "JP", "JP": "JP",
        "Spain": "ES", "Испания": "ES", "ES": "ES",
        "Estonia": "EE", "Эстония": "EE", "EE": "EE",
        "Finland": "FI", "Финляндия": "FI", "FI": "FI",
        "Sweden": "SE", "Швеция": "SE", "SE": "SE",
        "Canada": "CA", "Канада": "CA", "CA": "CA",
        "Singapore": "SG", "Сингапур": "SG", "SG": "SG",
        "India": "IN", "Индия": "IN", "IN": "IN",
    }
    for key, code in code_map.items():
        if key.lower() in location.lower():
            return code
    return "XX"


@app.get("/api/sub/{sub_token}")
def get_subscription(sub_token: str, db: Session = Depends(get_db)):
    """Публичный эндпоинт для мобильных приложений — возвращает список серверов для клиента"""
    client = db.query(ClientDB).filter_by(sub_token=sub_token).first()
    if not client:
        raise HTTPException(404, "Subscription not found")
    
    if not client.enabled:
        return {"status": "disabled", "servers": [], "message": "Подписка отключена"}
    
    if client.subscription_end and client.subscription_end < datetime.utcnow():
        return {"status": "expired", "servers": [], "message": "Подписка истекла"}
    
    # Build server list from nodes
    nodes = db.query(NodeDB).filter_by(is_online=True).all()
    servers = []
    
    def rewrite_key_for_node(shade_key: str, new_ip: str, new_port: int) -> str:
        """Rewrite server IP:port in a shade:// key for a different node.
        All nodes share the same crypto keys — only the server address changes."""
        try:
            b64 = shade_key.removeprefix("shade://")
            # Add padding back for standard base64 decode
            padded = b64 + "=" * (-len(b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded).decode())
            payload["s"] = f"{new_ip}:{new_port}"
            new_b64 = base64.urlsafe_b64encode(
                json.dumps(payload, separators=(',', ':')).encode()
            ).rstrip(b'=').decode()
            return f"shade://{new_b64}"
        except Exception:
            return shade_key  # Fallback to original if anything fails
    
    # Always include the primary server (from the client's existing key)
    if client.psk and client.psk.startswith("shade://"):
        servers.append({
            "id": "primary",
            "name": "Netherlands 🇳🇱",
            "country": "NL",
            "flag": "🇳🇱",
            "key": client.psk
        })
    
    # Add any additional nodes from the nodes table — each gets its own IP in the key
    for node in nodes:
        if node.ip_address == "185.204.52.135":
            continue  # Skip primary (already added above)
        flag = get_flag(node.location or node.name)
        country = get_country_code(node.location or node.name)
        node_key = rewrite_key_for_node(client.psk, node.ip_address, node.port) if client.psk else ""
        servers.append({
            "id": node.id,
            "name": f"{node.name} {flag}",
            "country": country,
            "flag": flag,
            "key": node_key
        })
    
    return {
        "status": "active",
        "username": client.name,
        "expires": client.subscription_end.strftime("%Y-%m-%d") if client.subscription_end else "unlimited",
        "dataUsage": round(client.data_usage, 2),
        "dataLimit": client.data_limit,
        "servers": servers
    }


# ═══════════════════  Rules  ═══════════════════

@app.get("/api/rules")
def list_rules(db: Session = Depends(get_db)):
    return [{
        "id": r.id, "name": r.name, "trigger": r.trigger,
        "action": r.action, "enabled": r.enabled,
    } for r in db.query(RuleDB).all()]


@app.post("/api/rules")
def create_rule(data: RuleCreate, db: Session = Depends(get_db)):
    rid = secrets.token_hex(4)
    r = RuleDB(id=rid, name=data.name, trigger=data.trigger,
               action=data.action, enabled=data.enabled)
    db.add(r); db.commit()
    return {"status": "created", "id": rid}


@app.patch("/api/rules/{rid}/toggle")
def toggle_rule(rid: str, body: RuleToggle, db: Session = Depends(get_db)):
    r = db.query(RuleDB).filter_by(id=rid).first()
    if not r: raise HTTPException(404)
    r.enabled = body.enabled; db.commit()
    return {"status": "toggled"}


@app.delete("/api/rules/{rid}")
def delete_rule(rid: str, db: Session = Depends(get_db)):
    r = db.query(RuleDB).filter_by(id=rid).first()
    if not r: raise HTTPException(404)
    db.delete(r); db.commit()
    return {"status": "deleted"}


# ═══════════════════  Settings  ═══════════════════

@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db)):
    return {r.key: r.value for r in db.query(SettingsDB).all()}


@app.post("/api/settings")
def update_settings(body: SettingsUpdate, db: Session = Depends(get_db)):
    for k, v in body.settings.items():
        row = db.query(SettingsDB).filter_by(key=k).first()
        if row: row.value = str(v)
        else: db.add(SettingsDB(key=k, value=str(v)))
    db.commit()
    return {"status": "saved"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8443, reload=True)
