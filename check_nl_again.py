import paramiko

nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

stdin, stdout, stderr = nl.exec_command("find / -name shadevpn.db 2>/dev/null")
print("DB paths:", stdout.read().decode().strip())

stdin, stdout, stderr = nl.exec_command("ps aux | grep uvicorn")
print("Uvicorn:", stdout.read().decode().strip())

stdin, stdout, stderr = nl.exec_command("curl -s file:///dev/null -speedtest-cli")
nl.exec_command("apt-get install -y jq curl")
stdin, stdout, stderr = nl.exec_command("curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3 -")
print("Speedtest:", stdout.read().decode().strip())

nl.close()
