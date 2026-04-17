import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

stdin, stdout, stderr = nl.exec_command("sqlite3 /opt/shadevpn/shadevpn-admin-backend/shadevpn.db \"SELECT psk FROM clients LIMIT 1;\"")
token = stdout.read().decode().strip().split('shade://')[1] if 'shade://' in stdout.read().decode() else "32d91fbf-eab1-4b25-8953-92d87cdfaccc"
# Wait, let me just run curl with the known token we used earlier: 32d91fbf-eab1-4b25-8953-92d87cdfaccc
stdin, stdout, stderr = nl.exec_command("curl -s http://localhost:8000/api/sub/32d91fbf-eab1-4b25-8953-92d87cdfaccc")
print(stdout.read().decode().strip())
nl.close()
