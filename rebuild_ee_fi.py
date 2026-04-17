import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

script = """#!/bin/bash
set -e
export PATH="$HOME/.cargo/bin:$PATH"
cd /opt/wowvpn
git reset --hard HEAD
git clean -fd
git pull origin master
cargo build --release -p aivpn-server

BIN_PATH=$(find /opt/wowvpn/target/release -name "aivpn-server" -not -name "*.d" | head -1)
if [ -z "$BIN_PATH" ]; then
    echo "ERROR BINARY NOT FOUND"
    exit 1
fi

cp "$BIN_PATH" /usr/local/bin/aivpn-server
chmod +x /usr/local/bin/aivpn-server

if [ ! -f /etc/shadevpn/tls-cert.pem ]; then
    openssl req -x509 -newkey rsa:2048 -keyout /etc/shadevpn/tls-key.pem -out /etc/shadevpn/tls-cert.pem -days 365 -nodes -subj '/CN=localhost'
fi

killall aivpn-server 2>/dev/null || true
pkill aivpn-server || true
sleep 1
nohup /usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json --transport both --tls-cert /etc/shadevpn/tls-cert.pem --tls-key /etc/shadevpn/tls-key.pem > /var/log/aivpn.log 2>&1 &
echo "SUCCESS"
"""

for ip, pw in [('150.241.101.56', '9z2fqj0frY8h'), ('2.26.91.190', 'QnJ2X4N9aJ6N')]:
    ssh = connect(ip, pw)
    stdin, stdout, stderr = ssh.exec_command("cat > /root/rebuild2.sh")
    stdin.write(script)
    stdin.channel.shutdown_write()
    ssh.exec_command("chmod +x /root/rebuild2.sh; nohup bash /root/rebuild2.sh > /root/rebuild2_log.txt 2>&1 &")
    ssh.close()
    print(f"Triggered for {ip}")
