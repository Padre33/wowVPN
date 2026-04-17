import paramiko, time

def connect(ip, pw):
    for i in range(3):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username='root', password=pw, timeout=10)
            return ssh
        except Exception:
            time.sleep(2)
    return None

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

print("EE:", run(connect('150.241.101.56', '9z2fqj0frY8h'), "tail -20 /root/rebuild2_log.txt"))
print("FI:", run(connect('2.26.91.190', 'QnJ2X4N9aJ6N'), "tail -20 /root/rebuild2_log.txt"))
