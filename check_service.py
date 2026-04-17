import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

stdin, stdout, stderr = nl.exec_command('cat /etc/systemd/system/shadevpn.service')
print("Netherlands Service:", stdout.read().decode().strip())

# Check running process on Estonia
stdin, stdout, stderr = nl.exec_command('sshpass -p 9z2fqj0frY8h ssh -o StrictHostKeyChecking=no root@150.241.101.56 "ps aux | grep aivpn"')
print("Estonia Service:", stdout.read().decode().strip())

nl.close()
