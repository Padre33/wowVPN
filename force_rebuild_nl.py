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

build = """nohup bash -c '
set -e
export PATH="$HOME/.cargo/bin:$PATH"
cd /opt/shadevpn
git reset --hard HEAD
git pull origin master
cargo build --release -p aivpn-server 2>&1 | tail -3
echo "NEW BIN: $(find target/release -name aivpn-server -not -name "*.d" 2>/dev/null | head -1)"
echo BUILD_COMPLETE
' > /opt/shadevpn/rebuild.log 2>&1 &"""

nl.exec_command(build)
print("Build started with force reset")
time.sleep(5)
print("Log:", run(nl, "tail -8 /opt/shadevpn/rebuild.log"))
nl.close()
