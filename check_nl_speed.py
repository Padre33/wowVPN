import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    return stdout.read().decode('utf-8', errors='replace').strip()

print("=== Testing NL raw bandwidth (iperf3) ===")
try:
    nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
    # Run iperf3 test to a public server (e.g., ping.online.net or speedtest)
    # Using speedtest-cli is easier for external bandwidth
    run(nl, "apt-get install -y speedtest-cli")
    print(run(nl, "speedtest-cli --simple"))
    nl.close()
except Exception as e:
    print("Error:", e)
