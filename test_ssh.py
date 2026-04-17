import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

stdin, stdout, stderr = nl.exec_command('ssh -o BatchMode=yes root@150.241.101.56 date')
print("Estonia:", stdout.read().decode().strip(), stderr.read().decode().strip())

stdin, stdout, stderr = nl.exec_command('ssh -o BatchMode=yes root@2.26.91.190 date')
print("Finland:", stdout.read().decode().strip(), stderr.read().decode().strip())
nl.close()
