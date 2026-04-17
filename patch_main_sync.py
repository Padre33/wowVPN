import paramiko

nl = paramiko.SSHClient()
nl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
nl.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)

script = """
import os

new_main_path = '/opt/shadevpn/shadevpn-admin-backend/main.py'
with open(new_main_path, 'r') as f:
    content = f.read()

# Replace systemctl restart shadevpn with syncing nodes
if 'os.system("systemctl restart shadevpn")' in content:
    content = content.replace('os.system("systemctl restart shadevpn")', 'os.system("systemctl restart shadevpn"); os.system("/opt/shadevpn/shadevpn-admin-backend/venv/bin/python3 /opt/shadevpn/shadevpn-admin-backend/push_nodes.py")')
    with open(new_main_path, 'w') as f:
        f.write(content)
    print("Patched main.py successfully")
    os.system("systemctl restart shadevpn-admin")
else:
    print("Already patched or not found")
"""

stdin, stdout, stderr = nl.exec_command(f'python3 -c "{script}"')
print("Patch main.py output:", stdout.read().decode().strip())
nl.close()
