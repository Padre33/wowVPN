import paramiko, base64, time

def connect_nl():
    for i in range(5):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)
            return ssh
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(10)
    raise Exception("Can't connect")

def run(ssh, cmd, decode=True):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read()
    err = stderr.read()
    if decode:
        return out.decode('utf-8', errors='replace'), err.decode('utf-8', errors='replace')
    return out, err

script = r"""
import os, subprocess

# Find ALL sqlite .db files on the server
result = subprocess.run(['find', '/', '-name', '*.db', '-not', '-path', '*/proc/*'], 
    capture_output=True, text=True, timeout=10)
print("ALL DB FILES:")
print(result.stdout)

# Find where the admin process is running from
result2 = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
for line in result2.stdout.splitlines():
    if 'uvicorn' in line or 'shadevpn' in line.lower() or 'python' in line:
        print("PROC:", line[:120])

# Check systemd service file
result3 = subprocess.run(['cat', '/etc/systemd/system/shadevpn-admin.service'], 
    capture_output=True, text=True)
print("SERVICE FILE:", result3.stdout)
"""

encoding = base64.b64encode(script.encode()).decode()
    
print("Connecting...")
ssh = connect_nl()
out, err = run(ssh, f"echo {encoding} | base64 -d | python3")
print(out)
if err:
    print("ERR:", err[:500])
ssh.close()
