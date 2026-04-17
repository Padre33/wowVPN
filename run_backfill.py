import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

sftp = nl.open_sftp()
sftp.put('backfill_sub_token.py', '/root/backfill_sub_token.py')
sftp.close()

stdin, stdout, stderr = nl.exec_command('python3 /root/backfill_sub_token.py')
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print("OUT:", out)
print("ERR:", err)
nl.close()
