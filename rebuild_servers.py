import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run(ssh, cmd, timeout=8):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    stdout.channel.settimeout(timeout)
    return stdout.read(4096).decode('utf-8', errors='replace')

# ─── NETHERLANDS: rebuild server binary with rate limit fix ───────────────────
nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')

# Pull latest code and rebuild in background
build_cmd = """nohup bash -c '
export PATH="$HOME/.cargo/bin:$PATH"
cd /opt/shadevpn
git pull origin master
cd aivpn-server
cargo build --release 2>&1 | tail -5
cp target/release/aivpn-server /opt/shadevpn/target/release/aivpn-server
systemctl restart shadevpn
echo BUILD_DONE
' > /opt/shadevpn/rebuild.log 2>&1 &"""

nl.exec_command(build_cmd)
print("Rebuild started on Netherlands (5-8 min)")

time.sleep(2)
out = run(nl, "tail -3 /opt/shadevpn/rebuild.log 2>/dev/null || echo 'starting...'")
print("Build log:", out)

nl.close()

# ─── ESTONIA: also rebuild to get same fix ────────────────────────────────────
print()
ee = connect('150.241.101.56', '9z2fqj0frY8h')
build_cmd_ee = """nohup bash -c '
export PATH="$HOME/.cargo/bin:$PATH"
if [ -d /opt/wowvpn ]; then
    cd /opt/wowvpn && git pull
else
    git clone https://github.com/Padre33/wowVPN.git /opt/wowvpn
fi
cd /opt/wowvpn/aivpn-server
cargo build --release 2>&1 | tail -5
cp target/release/aivpn-server /usr/local/bin/aivpn-server
kill -9 $(cat /var/run/aivpn.pid 2>/dev/null) 2>/dev/null
pkill aivpn-server || true; sleep 1
/usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json > /var/log/aivpn.log 2>&1 &
echo BUILD_DONE
' > /root/rebuild.log 2>&1 &"""

ee.exec_command(build_cmd_ee)
print("Estonia rebuild started")
time.sleep(2)
out = run(ee, "tail -3 /root/rebuild.log 2>/dev/null || echo 'starting...'")
print("Estonia build log:", out)
ee.close()
