import paramiko

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
    
    cmd = "date; /opt/shadevpn/target/release/aivpn-server --clients-db /etc/shadevpn/clients.json --list-clients"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    with open("rust_output.txt", "wb") as f:
        f.write(stdout.read())

except Exception as e:
    print("SSH fail:", e)
