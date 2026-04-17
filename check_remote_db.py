import paramiko

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
stdin, stdout, stderr = nl.exec_command("sqlite3 /opt/shadevpn/shadevpn-admin-backend/shadevpn.db 'SELECT id, name, location FROM nodes;'")
print("Remote DB:")
print(stdout.read().decode().strip())
nl.close()
