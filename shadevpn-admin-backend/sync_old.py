import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import ClientDB, Base
from datetime import datetime

DATABASE_URL = "sqlite:////opt/shadevpn/shadevpn-admin-backend/shadevpn.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def import_core_clients():
    try:
        with open("/etc/shadevpn/clients.json", "r") as f:
            core_data = json.load(f)
    except Exception as e:
        print(f"Ошибка чтения ядра: {e}")
        return

    db = SessionLocal()
    clients = core_data.get("clients", [])
    
    count = 0
    for c in clients:
        c_id = c.get("id")
        existing = db.query(ClientDB).filter_by(id=c_id).first()
        if not existing:
            # Восстанавливаем shade:// ссылку
            ip = c.get("vpn_ip", "10.0.0.X")
            psk = c.get("psk", "")
            shade_link = f"shade://{psk}@{ip}:443?name={c.get('name')}"
            
            new_client = ClientDB(
                id=c_id,
                name=c.get("name", "Unknown"),
                psk=shade_link,
                vpn_ip=ip,
                data_limit=100.0,  # Дефолт
                data_usage=0.0,
                telegram_id="",
                group_id=None,
                protocol="ShadeVPN",
                enabled=c.get("enabled", True),
                created_at=datetime.utcnow()
            )
            db.add(new_client)
            count += 1
            print(f"✅ Успешно импортирован клиент из Ядра в Админку: {c.get('name')}")
            
    db.commit()
    db.close()
    print(f"Готово. Добавлено {count} старых клиентов в таблицу Админки.")

if __name__ == "__main__":
    import_core_clients()
