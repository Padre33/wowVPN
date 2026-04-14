import paramiko
import os

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    
    sftp = ssh.open_sftp()
    
    LOCAL_SYNC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sync.py")
    sftp.put(LOCAL_SYNC, "/opt/shadevpn-admin/sync.py")
    
    sftp.close()
    
    print("Restarting service...")
    ssh.exec_command("systemctl restart shadevpn-admin")
    ssh.close()
    print("Done! sync.py uploaded.")
except Exception as e:
    print("Failed to deploy:", e)
