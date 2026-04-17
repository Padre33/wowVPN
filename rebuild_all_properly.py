import paramiko, time, sys

def connect(ip, pw):
    for i in range(3):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username='root', password=pw, timeout=10)
            return ssh
        except Exception as e:
            time.sleep(2)
    return None

def run_bg(ssh, script_content, log_file):
    stdin, stdout, stderr = ssh.exec_command(f"cat > /root/rebuild_script.sh")
    stdin.write(script_content)
    stdin.channel.shutdown_write()
    ssh.exec_command(f"chmod +x /root/rebuild_script.sh; nohup bash /root/rebuild_script.sh > {log_file} 2>&1 &")

# NL Script
script_nl = """#!/bin/bash
set -e
export PATH="$HOME/.cargo/bin:$PATH"
cd /opt/shadevpn
git reset --hard HEAD
git clean -fd
git pull origin master
cargo build --release -p aivpn-server
systemctl restart shadevpn
echo "NL_BUILD_OK"
"""

# EE Script
script_ee = """#!/bin/bash
set -e
export PATH="$HOME/.cargo/bin:$PATH"
cd /opt/wowvpn
git reset --hard HEAD
git clean -fd
git pull origin master
cd aivpn-server
cargo build --release
cp target/release/aivpn-server /usr/local/bin/aivpn-server
chmod +x /usr/local/bin/aivpn-server

# Gen TLS certs
if [ ! -f /etc/shadevpn/tls-cert.pem ]; then
    openssl req -x509 -newkey rsa:2048 -keyout /etc/shadevpn/tls-key.pem -out /etc/shadevpn/tls-cert.pem -days 365 -nodes -subj '/CN=localhost'
fi

killall aivpn-server 2>/dev/null || true
sleep 1
nohup /usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json --transport both --tls-cert /etc/shadevpn/tls-cert.pem --tls-key /etc/shadevpn/tls-key.pem > /var/log/aivpn.log 2>&1 &
echo "EE_BUILD_OK"
"""

# FI Script
script_fi = """#!/bin/bash
set -e
export PATH="$HOME/.cargo/bin:$PATH"
cd /opt/wowvpn
git reset --hard HEAD
git clean -fd
git pull origin master
cd aivpn-server
cargo build --release
cp target/release/aivpn-server /usr/local/bin/aivpn-server-linux
chmod +x /usr/local/bin/aivpn-server-linux

# Gen TLS certs
if [ ! -f /etc/shadevpn/tls-cert.pem ]; then
    openssl req -x509 -newkey rsa:2048 -keyout /etc/shadevpn/tls-key.pem -out /etc/shadevpn/tls-cert.pem -days 365 -nodes -subj '/CN=localhost'
fi

killall aivpn-server-linux 2>/dev/null || true
pkill aivpn-server || true
sleep 1
nohup /usr/local/bin/aivpn-server-linux --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json --transport both --tls-cert /etc/shadevpn/tls-cert.pem --tls-key /etc/shadevpn/tls-key.pem > /var/log/aivpn.log 2>&1 &
echo "FI_BUILD_OK"
"""

nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
if nl:
    print("Triggered NL")
    run_bg(nl, script_nl, "/root/rebuild_log.txt")
    nl.close()

ee = connect('150.241.101.56', '9z2fqj0frY8h')
if ee:
    print("Triggered EE")
    run_bg(ee, script_ee, "/root/rebuild_log.txt")
    ee.close()

fi = connect('2.26.91.190', 'QnJ2X4N9aJ6N')
if fi:
    print("Triggered FI")
    run_bg(fi, script_fi, "/root/rebuild_log.txt")
    fi.close()

print("All triggered. Waiting 1 minute...")
