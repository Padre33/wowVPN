import paramiko

nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

stdin, stdout, stderr = nl.exec_command("pid=$(pgrep uvicorn | head -1) && lsof -p $pid | grep \".db\"")
print("Open DBs:", stdout.read().decode().strip())
nl.close()
