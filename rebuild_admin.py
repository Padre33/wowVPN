import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

script = """
cd /opt/shadevpn/shadevpn-admin-backend
git fetch origin
git reset --hard origin/master
pkill uvicorn
sleep 1
nohup /opt/shadevpn/shadevpn-admin-backend/venv/bin/python3 /opt/shadevpn/shadevpn-admin-backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 > /var/log/uvicorn.log 2>&1 &
"""

stdin, stdout, stderr = nl.exec_command(script)
print(stdout.read().decode().strip())
nl.close()
