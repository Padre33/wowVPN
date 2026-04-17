import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

script = """
import paramiko
import os
import sqlite3

NODES = []
try:
    db = sqlite3.connect('/opt/shadevpn/shadevpn-admin-backend/shadevpn.db')
    c = db.cursor()
    c.execute("SELECT ip_address FROM nodes WHERE is_online=1")
    for row in c.fetchall():
        if row[0] != "185.204.52.135":
            NODES.append(row[0])
except Exception as e:
    print("DB error:", e)

PASSWORDS = {
    '150.241.101.56': '9z2fqj0frY8h',
    '2.26.91.190': 'QnJ2X4N9aJ6N'
}

for ip in NODES:
    pw = PASSWORDS.get(ip)
    if not pw: continue
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username='root', password=pw, timeout=10)
        sftp = ssh.open_sftp()
        sftp.put('/etc/shadevpn/clients.json', '/etc/shadevpn/clients.json')
        sftp.close()
        
        # Restart core to load new clients.json
        ssh.exec_command("pkill aivpn-server; sleep 1; nohup /usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json --transport both --tls-cert /etc/shadevpn/tls-cert.pem --tls-key /etc/shadevpn/tls-key.pem > /var/log/aivpn.log 2>&1 &")
        
        ssh.close()
        print(f"Synced and restarted {ip}")
    except Exception as e:
        print(f"Failed to sync {ip}: {e}")
"""
stdin, stdout, stderr = nl.exec_command(f'cat > /opt/shadevpn/shadevpn-admin-backend/push_nodes.py << "EOF"\n{script}\nEOF\n')
print(stdout.read().decode().strip(), stderr.read().decode().strip())
nl.close()
