import paramiko
import json

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    
    stdin, stdout, stderr = ssh.exec_command("systemctl status shadevpn --no-pager")
    status = stdout.read().decode("utf-8")
    
    stdin, stdout, stderr = ssh.exec_command("journalctl -u shadevpn -n 25 --no-pager")
    logs = stdout.read().decode("utf-8")
    
    with open("shadevpn_status.txt", "w", encoding="utf-8") as f:
        f.write("STATUS:\n" + status + "\n\nLOGS:\n" + logs)

except Exception as e:
    print("SSH fail:", e)
