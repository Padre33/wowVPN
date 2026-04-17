import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

script = """
import sqlite3
import uuid
db = sqlite3.connect('/opt/shadevpn/shadevpn-admin-backend/shadevpn.db')
c = db.cursor()
c.execute("SELECT id FROM clients WHERE sub_token IS NULL")
rows = c.fetchall()
for row in rows:
    c_id = row[0]
    sub_token = str(uuid.uuid4())
    c.execute("UPDATE clients SET sub_token = ? WHERE id = ?", (sub_token, c_id))
    print(f"Updated {c_id} with sub_token {sub_token}")
db.commit()
db.close()
"""
stdin, stdout, stderr = nl.exec_command(f'python3 -c "{script}"')
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print("OUT:", out)
print("ERR:", err)
nl.close()
