import paramiko
import os

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"
REMOTE_DIR = "/opt/shadevpn-admin"
LOCAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

def main():
    print("Uploading main.py to VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    
    sftp = ssh.open_sftp()
    sftp.put(LOCAL_FILE, f"{REMOTE_DIR}/main.py")
    sftp.close()
    
    print("Restarting service...")
    ssh.exec_command("systemctl restart shadevpn-admin")
    ssh.close()
    print("Done! Updated backend is running.")

if __name__ == "__main__":
    main()
