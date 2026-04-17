import paramiko

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

script = """
import sqlite3
db = sqlite3.connect('/opt/shadevpn/shadevpn-admin-backend/shadevpn.db')
c = db.cursor()
c.execute("SELECT id, name, ip_address, is_online FROM nodes")
print("NODES:")
for row in c.fetchall(): print(row)
"""

nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
stdin, stdout, stderr = nl.exec_command(f'python3 -c "{script}"')
print(stdout.read().decode().strip())
nl.close()
