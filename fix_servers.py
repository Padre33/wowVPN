import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run(ssh, cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    stdout.channel.settimeout(timeout)
    out = stdout.read(8192).decode('utf-8', errors='replace')
    err = stderr.read(4096).decode('utf-8', errors='replace')
    return out, err

# ─── ESTONIA: Restart via systemctl ───────────────────────────────────────────
print("=== ESTONIA fixing ===")
try:
    ee = connect('150.241.101.56', '9z2fqj0frY8h')
    
    # Check systemd service name
    out, _ = run(ee, "systemctl list-units --type=service | grep -i vpn | grep -i aivpn")
    print("Services:", out)
    
    # Find the service
    out, _ = run(ee, "systemctl list-units --type=service | grep aivpn")
    print("aivpn services:", out)
    
    # Try to restart via systemd
    out, err = run(ee, "systemctl restart aivpn-server 2>&1 || systemctl restart shadevpn 2>&1 || true")
    print("Systemd restart:", out, err)
    
    # Also try killing the process directly and not via signal
    out, _ = run(ee, "kill -9 4060 2>/dev/null; sleep 1; /usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json > /var/log/aivpn.log 2>&1 &")
    time.sleep(2)
    
    out, _ = run(ee, "ps aux | grep aivpn | grep -v grep | head -3")
    print("After fix:", out)
    
    # Test port
    out, _ = run(ee, "ss -ulnp sport = :443")
    print("Port 443:", out)
    
    ee.close()
except Exception as e:
    print(f"Estonia ERROR: {e}")

print()

# ─── FINLAND: Use existing prebuilt binary ────────────────────────────────────
print("=== FINLAND fixing ===")
try:
    fi = connect('2.26.91.190', 'QnJ2X4N9aJ6N')
    
    # Check the prebuilt binary
    out, _ = run(fi, "ls -la /opt/shadevpn/releases/aivpn-server")
    print("Prebuilt binary:", out)
    
    # Check if /etc/shadevpn exists with keys
    out, _ = run(fi, "ls /etc/shadevpn/ 2>/dev/null || echo 'NO DIR'")
    print("Keys dir:", out.strip())
    
    # Copy binary and setup
    run(fi, "cp /opt/shadevpn/releases/aivpn-server /usr/local/bin/aivpn-server; chmod +x /usr/local/bin/aivpn-server")
    
    # Start Finland server
    out, _ = run(fi, "pkill aivpn-server 2>/dev/null; sleep 1; /usr/local/bin/aivpn-server --listen 0.0.0.0:443 --key-file /etc/shadevpn/server.key --clients-db /etc/shadevpn/clients.json > /var/log/aivpn.log 2>&1 &")
    time.sleep(2)
    
    out, _ = run(fi, "ps aux | grep aivpn | grep -v grep")
    print("After start:", out)
    
    out, _ = run(fi, "ss -ulnp sport = :443")
    print("Port 443:", out)
    
    out, _ = run(fi, "tail -5 /var/log/aivpn.log")
    print("Log:", out)
    
    fi.close()
except Exception as e:
    print(f"Finland ERROR: {e}")

# ─── NETHERLANDS: Check raw throughput ───────────────────────────────────────
print()
print("=== NETHERLANDS: checking limits ===")
try:
    nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
    # Check if it's a VPS with bandwidth limit
    out, _ = run(nl, "cat /proc/net/dev | grep -v lo | head -5")
    print("NET stats:", out)
    
    # CPU info
    out, _ = run(nl, "nproc && cat /proc/cpuinfo | grep 'model name' | head -1")
    print("CPU:", out)
    
    nl.close()
except Exception as e:
    print(f"NL ERROR: {e}")
