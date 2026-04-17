import paramiko
import time

nodes = [
    ('185.204.52.135', 'qq%+@YHyrk{WFP$9'),  # NL
    ('150.241.101.56', '9z2fqj0frY8h'),      # EE
    ('87.120.16.241', 'EaeeDtwXgR4h')        # FI
]

for ip, pwd in nodes:
    print(f"Connecting to {ip}...")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username='root', password=pwd, timeout=10)
        
        # 1. Update systemd service to make MTU persistent
        service_fix = """[Unit]
Description=ShadeVPN Server (UDP + TLS)
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json --transport both --tls-cert /etc/shadevpn/tls-cert.pem --tls-key /etc/shadevpn/tls-key.pem
ExecStartPost=/bin/sh -c 'sleep 2 && ip link set dev aivpn0 mtu 1300'
Restart=always
RestartSec=5
LimitNOFILE=65535
Environment=RUST_LOG=info

[Install]
WantedBy=multi-user.target
"""
        if ip == '185.204.52.135':
            service_fix = service_fix.replace('/usr/local/bin/aivpn-server', '/opt/shadevpn/target/release/aivpn-server')
            
        sftp = client.open_sftp()
        with sftp.file('/etc/systemd/system/shadevpn.service', 'w') as f:
            f.write(service_fix)
        sftp.close()

        # 2. Reload and restart, wait 3 seconds, then verify MTU
        client.exec_command('systemctl daemon-reload')
        client.exec_command('systemctl restart shadevpn')
        time.sleep(4)
        
        # Check current MTU
        stdin, stdout, stderr = client.exec_command('ip link show dev aivpn0')
        out = stdout.read().decode().strip()
        print(f"{ip} MTU Status:", out)
        
        client.close()
    except Exception as e:
        print(f"Failed to connect to {ip}: {e}")
