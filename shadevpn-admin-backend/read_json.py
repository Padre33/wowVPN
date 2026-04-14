import paramiko
import json

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    
    stdin, stdout, stderr = ssh.exec_command("cat /etc/shadevpn/clients.json")
    out = stdout.read().decode("utf-8")
    
    try:
        data = json.loads(out)
        for c in data.get("clients", []):
            print(f"ID={c['id']}, Name={c['name']}")
    except Exception as e:
        print("Failed to parse JSON:", e)

except Exception as e:
    print("SSH fail:", e)
