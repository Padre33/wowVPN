import paramiko, time

def connect(ip, pw):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=10)
    return ssh

def run(ssh, cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    stdout.channel.settimeout(timeout)
    out = stdout.read(4096).decode('utf-8', errors='replace')
    return out

# ─── FINLAND: Check architecture and compile correct binary ───────────────────
print("=== FINLAND: Checking architecture ===")
fi = connect('2.26.91.190', 'QnJ2X4N9aJ6N')
print("Arch:", run(fi, "uname -m"))
print("OS:", run(fi, "cat /etc/os-release | head -3"))

# Trigger compilation in background (this will take 5-10 min)
# Use the correct target for this arch
setup_cmd = """
export PATH="$HOME/.cargo/bin:$PATH"
which cargo && echo "CARGO OK" || {
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    export PATH="$HOME/.cargo/bin:$PATH"
}
"""

# Check if rust already installed
rust_check = run(fi, "which cargo 2>/dev/null || echo NOT_INSTALLED")
print("Rust:", rust_check.strip())

# Check if binary exists from before at different location
bins = run(fi, "find / -name 'aivpn-server' -not -path '*/proc/*' 2>/dev/null | head -5")
print("Binaries:", bins)

# What's the actual arch
arch = run(fi, "uname -m").strip()
print(f"Architecture: {arch}")

fi.close()

# ─── NETHERLANDS: Fix the packet drops by tuning kernel settings ───────────────
print()
print("=== NETHERLANDS: Fix packet drops ===")
nl = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')

# Increase kernel UDP buffer and receive queue size
nl_fixes = """
# Increase socket receive buffer
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
sysctl -w net.core.rmem_default=134217728
sysctl -w net.core.wmem_default=134217728
sysctl -w net.core.netdev_max_backlog=65536
sysctl -w net.core.somaxconn=65536
sysctl -w net.ipv4.udp_rmem_min=8192
sysctl -w net.ipv4.udp_wmem_min=8192
echo "Kernel tuning applied"
"""
cmd = "sysctl -w net.core.rmem_max=134217728; sysctl -w net.core.wmem_max=134217728; sysctl -w net.core.netdev_max_backlog=65536; echo DONE"
out = run(nl, cmd)
print("Kernel tuning:", out)

# Check drops before/after
out = run(nl, "cat /proc/net/dev | grep tunb")
print("TUN drops:", out)

nl.close()
