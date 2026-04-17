import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run(ssh, cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    stdout.channel.settimeout(timeout)
    return stdout.read(4096).decode('utf-8', errors='replace')

fi = connect('2.26.91.190', 'QnJ2X4N9aJ6N')

# Finland is x86_64 so our binary SHOULD work. 
# But it says "Exec format error" - check the binary type
out = run(fi, "file /opt/shadevpn/releases/aivpn-server")
print("Binary type:", out)

out = run(fi, "file /opt/shadevpn/aivpn-server")
print("aivpn-server type:", out)

# Try running the OTHER binary  
out = run(fi, "/opt/shadevpn/aivpn-server --help 2>&1 | head -3")
print("aivpn-server test:", out)

# Check if there's a musl vs glibc issue
out = run(fi, "ldd /opt/shadevpn/releases/aivpn-server 2>&1 | head -5")
print("ldd:", out)

fi.close()
