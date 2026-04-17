import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

script = """
import sqlite3
db = sqlite3.connect('/opt/shadevpn/shadevpn-admin-backend/shadevpn.db')
c = db.cursor()
c.execute("SELECT name, sub_token FROM clients")
for row in c.fetchall(): print(row)
"""
stdin, stdout, stderr = nl.exec_command(f'python3 -c "{script}"')
print(stdout.read().decode().strip())
nl.close()
