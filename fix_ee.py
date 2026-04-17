import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    return stdout.read().decode('utf-8', errors='replace').strip()

print("=== EE (Fixing text file busy) ===")
ee = connect('150.241.101.56', '9z2fqj0frY8h')
print(run(ee, "killall aivpn-server; pkill aivpn-server; systemctl stop aivpn-server || true; sleep 2"))
print(run(ee, "cp /opt/wowvpn/target/release/aivpn-server /usr/local/bin/aivpn-server"))
print(run(ee, "nohup /usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json --transport both --tls-cert /etc/shadevpn/tls-cert.pem --tls-key /etc/shadevpn/tls-key.pem > /var/log/aivpn.log 2>&1 &"))
time.sleep(2)
print("EE running:", run(ee, "ps aux | grep aivpn | grep -v grep"))
print("EE ports:", run(ee, "ss -tlpn sport = :443; ss -ulpn sport = :443"))
ee.close()

print("\n=== FI (Checking status) ===")
fi = connect('2.26.91.190', 'QnJ2X4N9aJ6N')
print("FI running:", run(fi, "ps aux | grep aivpn | grep -v grep"))
print("FI ports:", run(fi, "ss -tlpn sport = :443; ss -ulpn sport = :443"))
fi.close()

print("\n=== NL (Checking status) ===")
nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
print("NL limits test:", run(nl, "cat /proc/$(pgrep aivpn-server | head -1)/cmdline 2>/dev/null | tr '\\0' ' '"))
nl.close()
