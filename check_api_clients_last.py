import paramiko
import json

nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

script = """
import urllib.request
import json
req = urllib.request.Request('http://127.0.0.1:8000/api/clients')
try:
    with urllib.request.urlopen(req) as resp:
        clients = json.loads(resp.read())
        # Print the last 2 clients
        for c in clients[-2:]:
            print(c['username'], c.get('sub_token', 'NONE'), c.get('shadeLink', 'NONE')[:40])
except Exception as e:
    print('Failed:', e)
"""
stdin, stdout, stderr = nl.exec_command(f'python3 -c "{script}"')
print("API returned:", stdout.read().decode().strip())
nl.close()
