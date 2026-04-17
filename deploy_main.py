import paramiko, time, os

LOCAL_MAIN = r"C:\Users\user\Desktop\contract checker\wowVPN_repo\shadevpn-admin-backend\main.py"
REMOTE_MAIN = "/opt/shadevpn/shadevpn-admin-backend/main.py"

def connect():
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

ssh = connect()

print("Uploading main.py...")
sftp = ssh.open_sftp()
sftp.put(LOCAL_MAIN, REMOTE_MAIN)
sftp.close()
print("Uploaded!")

print("Restarting admin service...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shadevpn-admin; sleep 3; systemctl is-active shadevpn-admin")
result = stdout.read().decode().strip()
print(f"Service status: {result}")

# Test the API
print("Testing API...")
token = "32d91fbf-eab1-4b25-8953-92d87cdfaccc"
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/sub/{token}")
import json
out = stdout.read().decode('utf-8', errors='replace')
try:
    data = json.loads(out)
    print(f"Status: {data.get('status')}")
    for s in data.get('servers', []):
        print(f"  {s['name']} -> key IP: {s['key'][7:] if s.get('key') else 'NO KEY'}")
        # Decode key to show server IP
        import base64
        try:
            b64 = s['key'].replace('shade://', '')
            padded = b64 + "=" * (-len(b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded).decode())
            print(f"    Server addr: {payload.get('s')}")
        except:
            pass
except Exception as e:
    print("Raw:", out[:500])

ssh.close()
