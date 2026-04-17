import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

stdin, stdout, stderr = client.exec_command('journalctl -u shadevpn -n 20 --no-pager')
print("Logs:", stdout.read().decode().strip())
client.close()
