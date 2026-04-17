import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run_bg(ssh, cmd):
    """Run in background and return immediately"""
    ssh.exec_command(cmd)

fi = connect('2.26.91.190', 'QnJ2X4N9aJ6N')

# Check if our git repo is already cloned  
stdin, stdout, stderr = fi.exec_command("ls /opt/shadevpn/aivpn-server/Cargo.toml 2>/dev/null && echo EXISTS || echo NOT_FOUND", timeout=5)
print("Repo check:", stdout.read(200).decode().strip())

# Nuke everything and clone fresh + compile
build_script = """#!/bin/bash
set -e
export PATH="$HOME/.cargo/bin:$PATH"

# Clone repo if not present
if [ ! -d /opt/wowvpn ]; then
    git clone https://github.com/Padre33/wowVPN.git /opt/wowvpn
fi
cd /opt/wowvpn

# Pull latest
git pull

# Build the server
cd aivpn-server
cargo build --release

# Copy binary
cp target/release/aivpn-server /usr/local/bin/aivpn-server-linux
chmod +x /usr/local/bin/aivpn-server-linux
echo "BUILD DONE!"
"""

# Write and run script
stdin, stdout, stderr = fi.exec_command("cat > /root/build_server.sh", timeout=5)
stdin.write(build_script)
stdin.channel.shutdown_write()

fi.exec_command("chmod +x /root/build_server.sh; nohup bash /root/build_server.sh > /root/build_log.txt 2>&1 &")
print("Compilation started in background! Will take 5-8 minutes.")
print("Check progress: tail -f /root/build_log.txt")

time.sleep(2)

# Show first lines
stdin, stdout, stderr = fi.exec_command("tail -5 /root/build_log.txt 2>/dev/null", timeout=5)
print("Current log:", stdout.read(500).decode())

fi.close()
