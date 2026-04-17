import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

stdin, stdout, stderr = nl.exec_command('/opt/shadevpn/shadevpn-admin-backend/venv/bin/python3 /opt/shadevpn/shadevpn-admin-backend/push_nodes.py')
print(stdout.read().decode().strip(), stderr.read().decode().strip())
nl.close()
