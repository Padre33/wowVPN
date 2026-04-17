import paramiko
import os
import time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

try:
    print("Fetching master keys from Netherlands...")
    ssh_nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
    
    # Check if folder exists, if not create & initialize Default!
    ssh_nl.exec_command("mkdir -p /etc/shadevpn")
    
    # Test if server.key exists
    stdin, stdout, stderr = ssh_nl.exec_command("cat /etc/shadevpn/server.key | base64")
    b64_key = stdout.read().decode().strip()
    
    if not b64_key:
        print("server.key missing on NL! Creating a new one...")
        ssh_nl.exec_command("openssl rand 32 > /etc/shadevpn/server.key")
        time.sleep(1)
        stdin, stdout, stderr = ssh_nl.exec_command("cat /etc/shadevpn/server.key | base64")
        b64_key = stdout.read().decode().strip()
        
    stdin, stdout, stderr = ssh_nl.exec_command("cat /etc/shadevpn/clients.json")
    clients = stdout.read().decode().strip()
    if not clients:
        clients = "[]"
        ssh_nl.exec_command("echo '[]' > /etc/shadevpn/clients.json")
        
    print(f"Got master key (b64 length: {len(b64_key)}). Clients: {clients[:50]}...")
    
    # Restart NL server properly!
    ssh_nl.exec_command("killall aivpn-server")
    time.sleep(1)
    ssh_nl.exec_command("nohup /opt/shadevpn/target/release/aivpn-server --listen 0.0.0.0:443 --transport both --clients-db /etc/shadevpn/clients.json --key-file /etc/shadevpn/server.key > /opt/shadevpn/server_vpn.log 2>&1 &")
    print("NL Server restarted successfully!")
    
    # Deploy to Estonia and Finland
    nodes = [
        ('Estonia', '150.241.101.56', '9z2fqj0frY8h'),
        ('Finland', '2.26.91.190', 'QnJ2X4N9aJ6N')
    ]
    
    # Setup Script for nodes
    setup_script = f"""
    mkdir -p /etc/shadevpn
    echo "{b64_key}" | base64 -d > /etc/shadevpn/server.key
    cat << 'EOF' > /etc/shadevpn/clients.json
{clients}
EOF
    apt update && apt install -y curl build-essential git iptables
    
    if [ ! -d "/opt/shadevpn" ]; then
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        export PATH="$HOME/.cargo/bin:$PATH"
        git clone https://github.com/Padre33/wowVPN.git /opt/shadevpn
        cd /opt/shadevpn/aivpn-server && cargo build --release
    fi
    
    killall aivpn-server || true
    nohup /opt/shadevpn/target/release/aivpn-server --listen 0.0.0.0:443 --transport both --clients-db /etc/shadevpn/clients.json --key-file /etc/shadevpn/server.key > /opt/shadevpn/server_vpn.log 2>&1 &
    
    echo "Node setup finished!"
    """
    
    for name, ip, pw in nodes:
        print(f"Deploying to {name} ({ip})... (this will take 5-10 minutes for rust compilation)")
        ssh_node = connect(ip, pw)
        # Execute in background via nohup, we will check status later
        stdin, stdout, stderr = ssh_node.exec_command(f"nohup bash -c '{setup_script.replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}' > /root/deploy.log 2>&1 &")
        print(f"Triggered setup on {name}")
        ssh_node.close()
        
    print("All deployments triggered!")
        
except Exception as e:
    import traceback
    traceback.print_exc()
