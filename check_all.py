import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run(ssh, cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

print("=== NETHERLANDS (Checking Rebuild) ===")
try:
    nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
    print("Rebuild Log:")
    print(run(nl, "tail -10 /opt/shadevpn/rebuild.log"))
    print("\nRunning Process:")
    print(run(nl, "ps aux | grep aivpn | grep -v grep"))
    print("\nBinary modification time:")
    print(run(nl, "stat -c '%y %n' /opt/shadevpn/target/release/aivpn-server"))
    nl.close()
except Exception as e:
    print(f"NL ERROR: {e}")

print("\n=== ESTONIA (Fixing TLS & Restarting) ===")
try:
    ee = connect('150.241.101.56', '9z2fqj0frY8h')
    
    # Check if certs exist, generate if not
    run(ee, "if [ ! -f /etc/shadevpn/tls-cert.pem ]; then openssl req -x509 -newkey rsa:2048 -keyout /etc/shadevpn/tls-key.pem -out /etc/shadevpn/tls-cert.pem -days 365 -nodes -subj '/CN=localhost'; fi")
    
    # Kill and restart WITH TLS
    run(ee, "kill -9 $(pgrep aivpn-server) 2>/dev/null; sleep 1")
    run(ee, "nohup /usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json --transport both --tls-cert /etc/shadevpn/tls-cert.pem --tls-key /etc/shadevpn/tls-key.pem > /var/log/aivpn.log 2>&1 &")
    
    time.sleep(2)
    print("Running Process:")
    print(run(ee, "ps aux | grep aivpn | grep -v grep"))
    print("Ports listening:")
    print(run(ee, "ss -ulnp | grep 443; ss -tlnp | grep 443"))
    ee.close()
except Exception as e:
    print(f"EE ERROR: {e}")

print("\n=== FINLAND (Checking Compile & Fixing TLS) ===")
try:
    fi = connect('2.26.91.190', 'QnJ2X4N9aJ6N')
    print("Compile Log:")
    print(run(fi, "tail -10 /root/build_log.txt 2>/dev/null"))
    
    # Check if binary was successfully built and copied
    has_bin = run(fi, "ls -la /usr/local/bin/aivpn-server-linux 2>/dev/null")
    print("\nBinary Built?", has_bin)
    
    if "aivpn-server-linux" in has_bin:
        # Generate certs
        run(fi, "if [ ! -f /etc/shadevpn/tls-cert.pem ]; then openssl req -x509 -newkey rsa:2048 -keyout /etc/shadevpn/tls-key.pem -out /etc/shadevpn/tls-cert.pem -days 365 -nodes -subj '/CN=localhost'; fi")
        
        # Restart
        run(fi, "kill -9 $(pgrep aivpn-server) 2>/dev/null; sleep 1")
        run(fi, "nohup /usr/local/bin/aivpn-server-linux --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json --transport both --tls-cert /etc/shadevpn/tls-cert.pem --tls-key /etc/shadevpn/tls-key.pem > /var/log/aivpn.log 2>&1 &")
        
        time.sleep(2)
        print("\nRunning Process:")
        print(run(fi, "ps aux | grep aivpn | grep -v grep"))
        print("Ports listening:")
        print(run(fi, "ss -ulnp | grep 443; ss -tlnp | grep 443"))
    fi
    fi.close()
except Exception as e:
    print(f"FI ERROR: {e}")
