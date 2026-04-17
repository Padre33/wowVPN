import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

sftp = nl.open_sftp()
sftp.put('./shadevpn-admin-backend/main.py', '/opt/shadevpn/shadevpn-admin-backend/main.py')
sftp.close()

stdin, stdout, stderr = nl.exec_command('systemctl restart shadevpn-admin')
print("Restart backend output:", stdout.read().decode().strip(), stderr.read().decode().strip())
nl.close()
