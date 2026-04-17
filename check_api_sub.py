import paramiko
nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

script = """
import urllib.request
import json
req = urllib.request.Request('http://127.0.0.1:8000/api/clients')
try:
    with urllib.request.urlopen(req) as resp:
        for c in json.loads(resp.read()):
            if 'padre' in c['username']:
                print(c['username'], c['shadeLink'])
except Exception as e:
    print('Failed:', e)
"""
stdin, stdout, stderr = nl.exec_command(f'python3 -c "{script}"')
print("API returned:", stdout.read().decode().strip())
nl.close()
