import paramiko
import json
from datetime import datetime

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    
    stdin, stdout, stderr = ssh.exec_command("cat /etc/shadevpn/clients.json")
    out = stdout.read().decode("utf-8")
    
    data = json.loads(out)
    for c in data.get("clients", []):
        stats = c.get("stats", {})
        last_h = stats.get("last_handshake", "")
        if last_h:
            h_str = last_h.replace("Z", "").split(".")[0]
            dt = datetime.strptime(h_str, "%Y-%m-%dT%H:%M:%S")
            now_utc = datetime.utcnow()
            diff = (now_utc - dt).total_seconds()
            print(f"[{c['name']}] Handshake: {h_str} UTC | Now: {now_utc.strftime('%Y-%m-%dT%H:%M:%S')} UTC | Diff: {diff:.1f}s | Online: {diff < 300}")
        else:
            print(f"[{c['name']}] No handshake")

except Exception as e:
    print("SSH fail:", e)
