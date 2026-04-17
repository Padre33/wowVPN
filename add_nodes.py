import paramiko
import uuid
import base64

py_script = '''
import sqlite3
import uuid

conn = sqlite3.connect("/opt/shadevpn-admin/shadevpn.db")
c = conn.cursor()
c.execute("INSERT OR IGNORE INTO nodes (id, name, location, ip_address, port, is_online) VALUES (?, ?, ?, ?, ?, ?)", (str(uuid.uuid4()), "Estonia 1G", "Estonia", "150.241.101.56", 443, True))
c.execute("INSERT OR IGNORE INTO nodes (id, name, location, ip_address, port, is_online) VALUES (?, ?, ?, ?, ?, ?)", (str(uuid.uuid4()), "Finland Power", "Finland", "2.26.91.190", 443, True))
conn.commit()
print("DB ok")
'''

encoded = base64.b64encode(py_script.encode()).decode()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9')

stdin, stdout, stderr = ssh.exec_command(f"echo {encoded} | base64 -d | python3")
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
