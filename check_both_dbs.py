import paramiko

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

script = """
import sqlite3
import os

for db_path in ['/opt/shadevpn/shadevpn-admin-backend/shadevpn.db', '/opt/shadevpn-admin/shadevpn.db']:
    if os.path.exists(db_path):
        print(f"\\n--- DB: {db_path} ---")
        try:
            db = sqlite3.connect(db_path)
            c = db.cursor()
            c.execute("SELECT id, name, location, ip_address FROM nodes")
            for row in c.fetchall(): print(row)
        except Exception as e:
            print("Error:", e)
"""

nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
stdin, stdout, stderr = nl.exec_command(f'python3 -c "{script}"')
print(stdout.read().decode().strip())
nl.close()
