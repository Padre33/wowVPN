import paramiko, time, sys

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    stdout.channel.settimeout(10)
    out = stdout.read(4096).decode('utf-8', errors='replace')
    return out

# ─── ESTONIA ──────────────────────────────────────────────────────────────────
print("ESTONIA:")
try:
    ee = connect('150.241.101.56', '9z2fqj0frY8h')
    print(" PROC:", run(ee, "ps aux | grep aivpn | grep -v grep | head -2"))
    print(" KEY bytes:", run(ee, "wc -c /etc/shadevpn/server.key"))
    # Kill and restart
    run(ee, "killall aivpn-server 2>/dev/null; sleep 1")
    ee.exec_command("/usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json > /var/log/aivpn.log 2>&1 &")
    time.sleep(2)
    print(" AFTER RESTART:", run(ee, "ps aux | grep aivpn | grep -v grep | head -2"))
    ee.close()
    print(" OK")
except Exception as e:
    print(f" ERROR: {e}")

print()
print("FINLAND:")
try:
    fi = connect('2.26.91.190', 'QnJ2X4N9aJ6N')
    print(" DEPLOY LOG:", run(fi, "tail -5 /root/deploy.log 2>/dev/null"))
    print(" BINARY:", run(fi, "find /opt /usr/local/bin -name 'aivpn-server' 2>/dev/null | head -3"))
    print(" CARGO:", run(fi, "ps aux | grep cargo | grep -v grep | head -2"))
    fi.close()
except Exception as e:
    print(f" ERROR: {e}")

print()
print("NETHERLANDS server log:")
try:
    nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
    print(run(nl, "tail -15 /opt/shadevpn/server_vpn.log 2>/dev/null || echo 'no log'"))
    print(" VPN PROC:", run(nl, "ps aux | grep 'aivpn-server' | grep -v grep | head -2"))
    nl.close()
except Exception as e:
    print(f" ERROR: {e}")
