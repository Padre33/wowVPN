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

nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')

# Check existing binary PPS
print("Current running args:", run(nl, "cat /proc/$(pgrep aivpn-server | head -1)/cmdline 2>/dev/null | tr '\\0' ' '"))

# Path inspection
print("Repo structure:", run(nl, "ls /opt/shadevpn/"))
print("Current binary:", run(nl, "ls -la /opt/shadevpn/target/release/aivpn-server 2>/dev/null || echo NOT_FOUND"))

# Pull and rebuild from correct path
build = """nohup bash -c '
set -e
export PATH="$HOME/.cargo/bin:$PATH"
cd /opt/shadevpn
git pull origin master
cargo build --release -p aivpn-server 2>&1 | tail -5
NEW_BIN=$(find /opt/shadevpn/target/release -name "aivpn-server" -not -name "*.d" | head -1)
echo "Found binary: $NEW_BIN"
if [ -f "$NEW_BIN" ]; then
    cp "$NEW_BIN" /usr/local/bin/aivpn-server-new
    chmod +x /usr/local/bin/aivpn-server-new
    echo BUILD_COMPLETE
else
    echo "BUILD FAILED - binary not found"
fi
' > /opt/shadevpn/rebuild.log 2>&1 &"""

nl.exec_command(build)
print("Rebuild re-triggered")

time.sleep(3)
print("Log:", run(nl, "tail -5 /opt/shadevpn/rebuild.log"))
nl.close()
