import os, uuid
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///./shadevpn.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ClientDB(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    telegram_id = Column(String, nullable=True)
    psk = Column(String, nullable=False)
    vpn_ip = Column(String, nullable=False)
    protocol = Column(String, default="ShadeVPN")
    data_usage = Column(Float, default=0.0)
    data_limit = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription_end = Column(DateTime, nullable=True)
    enabled = Column(Boolean, default=True)
    group_id = Column(String, nullable=True)  # FK to groups
    sub_token = Column(String, nullable=True, unique=True)  # Subscription token for dynamic server list


class GroupDB(Base):
    __tablename__ = "groups"
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default="")
    data_limit = Column(String, default="100 ГБ/юзер")
    created_at = Column(DateTime, default=datetime.utcnow)


class TemplateDB(Base):
    __tablename__ = "templates"
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    duration_days = Column(Integer, default=30)
    data_limit_gb = Column(Float, default=50.0)
    price = Column(String, default="0")
    created_at = Column(DateTime, default=datetime.utcnow)


class NodeDB(Base):
    __tablename__ = "nodes"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, default="")
    ip_address = Column(String, default="")
    port = Column(Integer, default=443)
    is_online = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RuleDB(Base):
    __tablename__ = "rules"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    trigger = Column(String, nullable=False)
    action = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrafficSnapshotDB(Base):
    """Снапшот трафика — записывается каждые 5 минут фоновой задачей"""
    __tablename__ = "traffic_snapshots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String, nullable=False, index=True)
    bytes_in = Column(Float, default=0.0)
    bytes_out = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class SettingsDB(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)


Base.metadata.create_all(bind=engine)

# ── Auto-migration: add missing columns to existing tables ──
import sqlite3 as _sq
_conn = _sq.connect("./shadevpn.db")
_cur = _conn.cursor()
_cur.execute("PRAGMA table_info(clients)")
_existing_cols = {row[1] for row in _cur.fetchall()}
if "group_id" not in _existing_cols:
    _cur.execute("ALTER TABLE clients ADD COLUMN group_id TEXT")
    _conn.commit()
    print("[MIGRATION] Added 'group_id' column to 'clients' table")
if "sub_token" not in _existing_cols:
    _cur.execute("ALTER TABLE clients ADD COLUMN sub_token TEXT")
    _conn.commit()
    print("[MIGRATION] Added 'sub_token' column to 'clients' table")
    # Generate sub_token for existing clients that don't have one
    _cur.execute("SELECT id FROM clients WHERE sub_token IS NULL")
    _rows = _cur.fetchall()
    for _row in _rows:
        _cur.execute("UPDATE clients SET sub_token=? WHERE id=?", (str(uuid.uuid4()), _row[0]))
    if _rows:
        _conn.commit()
        print(f"[MIGRATION] Generated sub_token for {len(_rows)} existing clients")
_conn.close()

# Seed defaults
_s = SessionLocal()
for k, v in {
    "server_ip": "185.204.52.135",
    "server_port": "443",
    "stealth_domain": "www.apple.com",
    "logging_enabled": "true",
    "telegram_bot_token": "",
    "telegram_admin_chat_id": "",
    "server_public_key": "o20mBO1hviMoLLm/Rt3ToyHc8rk4sXTak28tHYqqu74=",
}.items():
    if not _s.query(SettingsDB).filter_by(key=k).first():
        _s.add(SettingsDB(key=k, value=v))
_s.commit()
_s.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
