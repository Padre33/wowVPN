import paramiko
import os

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"

script = """
from database import SessionLocal, TrafficSnapshotDB

def clear_snapshots():
    db = SessionLocal()
    try:
        deleted = db.query(TrafficSnapshotDB).delete()
        db.commit()
        print(f"Deleted {deleted} bloated snapshots.")
    except Exception as e:
        print("Error:", e)
    finally:
        db.close()

clear_snapshots()
"""

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    
    # Upload clear script
    sftp = ssh.open_sftp()
    with sftp.open("/opt/shadevpn-admin/fix_bloat.py", "w") as f:
        f.write(script)
    
    # Upload main.py
    LOCAL_MAIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    sftp.put(LOCAL_MAIN, "/opt/shadevpn-admin/main.py")
    
    sftp.close()
    
    print("Running fix_bloat.py on VPS...")
    stdin, stdout, stderr = ssh.exec_command("cd /opt/shadevpn-admin && venv/bin/python fix_bloat.py")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    print("Restarting service...")
    ssh.exec_command("systemctl restart shadevpn-admin")
    ssh.close()
    print("Deploy complete!")
except Exception as e:
    print("Failed:", e)
