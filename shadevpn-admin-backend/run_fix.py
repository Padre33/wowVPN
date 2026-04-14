import paramiko
import os

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"

script = """
import json
from datetime import datetime
from database import SessionLocal, ClientDB

def sync():
    db = SessionLocal()
    try:
        with open("/etc/shadevpn/clients.json", "r") as f:
            data = json.load(f)
            
        # Clean existing
        db.query(ClientDB).delete()
        db.commit()
        
        # Import from JSON
        for c in data.get("clients", []):
            new_c = ClientDB(
                id=c["id"],
                name=c["name"],
                psk=c["psk"],
                vpn_ip=c["vpn_ip"],
                protocol="ShadeVPN",
                enabled=c.get("enabled", True),
            )
            db.add(new_c)
        db.commit()
        print("Sync complete. Re-imported", len(data.get("clients", [])), "clients.")
    except Exception as e:
        print("Error:", e)
    finally:
        db.close()

sync()
"""

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    
    sftp = ssh.open_sftp()
    with sftp.open("/opt/shadevpn-admin/fix_sync.py", "w") as f:
        f.write(script)
    sftp.close()
    
    print("Running fix_sync.py on VPS...")
    stdin, stdout, stderr = ssh.exec_command("cd /opt/shadevpn-admin && venv/bin/python fix_sync.py")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()
except Exception as e:
    print("Failed:", e)
