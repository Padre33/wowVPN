# -*- coding: utf-8 -*-
"""
ShadeVPN Auto-Deploy Script
"""
import paramiko
import os
import sys
import time

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VPS_IP = "185.204.52.135"
VPS_USER = "root"
VPS_PASS = r"qq%+@YHyrk{WFP$9"
REMOTE_DIR = "/opt/shadevpn-admin"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

FILES_TO_UPLOAD = ["main.py", "database.py", "sync.py", "requirements.txt"]


def run_cmd(ssh, cmd, label=""):
    print(f"\n--- {label or cmd} ---")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out.strip():
        print(out.strip())
    if err.strip() and "WARNING" not in err:
        print(f"[ERR] {err.strip()}")
    return out, err


def main():
    print("=" * 60)
    print("  ShadeVPN Auto-Deploy")
    print(f"  VPS: {VPS_IP}")
    print("=" * 60)

    # 1. Connect
    print("\n[1/7] Connecting to VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
        print("  OK - Connected!")
    except Exception as e:
        print(f"  FAIL: {e}")
        sys.exit(1)

    # 2. Recon
    print("\n[2/7] Analyzing server...")
    run_cmd(ssh, "uname -a", "OS Version")
    run_cmd(ssh, "which python3 || echo 'NO PYTHON3'", "Python3")
    out, _ = run_cmd(ssh, "find / -name 'clients.json' -type f 2>/dev/null | head -10", "Finding clients.json")
    clients_json_paths = [p.strip() for p in out.strip().split("\n") if p.strip()]
    print(f"  Found: {clients_json_paths}")

    run_cmd(ssh, "docker ps --format '{{.Names}} {{.Image}}' 2>/dev/null || echo 'NO_DOCKER'", "Docker containers")

    # Pick clients.json path
    clients_json = ""
    for p in clients_json_paths:
        if "/opt/shadevpn-admin/" not in p:
            clients_json = p
            break

    if not clients_json:
        for path in ["/etc/aivpn/clients.json", "/root/aivpn/clients.json", "/var/lib/aivpn/clients.json"]:
            test_out, _ = run_cmd(ssh, f"test -f {path} && echo EXISTS || echo NOPE", f"Check {path}")
            if "EXISTS" in test_out:
                clients_json = path
                break

    if clients_json:
        print(f"\n  >> clients.json: {clients_json}")
    else:
        clients_json = "/etc/aivpn/clients.json"
        print(f"\n  >> Using default: {clients_json}")

    # 3. Install Python
    print("\n[3/7] Installing Python...")
    run_cmd(ssh, "apt-get update -yqq 2>&1 | tail -1 && apt-get install -y python3 python3-pip python3-venv 2>&1 | tail -3", "apt install")

    # 4. Upload files
    print("\n[4/7] Uploading files...")
    run_cmd(ssh, f"mkdir -p {REMOTE_DIR}", "mkdir")

    sftp = ssh.open_sftp()
    for fname in FILES_TO_UPLOAD:
        local_path = os.path.join(LOCAL_DIR, fname)
        remote_path = f"{REMOTE_DIR}/{fname}"
        if os.path.exists(local_path):
            sftp.put(local_path, remote_path)
            fsize = os.path.getsize(local_path)
            print(f"  OK: {fname} ({fsize} bytes)")
        else:
            print(f"  MISSING: {local_path}")
    sftp.close()

    # 5. Setup venv
    print("\n[5/7] Setting up Python venv...")
    run_cmd(ssh, f"cd {REMOTE_DIR} && python3 -m venv venv 2>&1 | tail -2", "Create venv")
    run_cmd(ssh, f"cd {REMOTE_DIR} && source venv/bin/activate && pip install -r requirements.txt 2>&1 | tail -5", "pip install")

    # 6. Create systemd service
    print("\n[6/7] Creating systemd service...")
    service = (
        "[Unit]\n"
        "Description=ShadeVPN Admin Backend\n"
        "After=network.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        "User=root\n"
        f"WorkingDirectory={REMOTE_DIR}\n"
        f'Environment="AIVPN_CLIENTS_JSON={clients_json}"\n'
        f"ExecStart={REMOTE_DIR}/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8443\n"
        "Restart=always\n"
        "RestartSec=5\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
    )
    # Write via sftp
    sftp = ssh.open_sftp()
    with sftp.open("/etc/systemd/system/shadevpn-admin.service", "w") as f:
        f.write(service)
    sftp.close()
    print("  OK: service file written")

    run_cmd(ssh, "systemctl daemon-reload", "daemon-reload")
    run_cmd(ssh, "systemctl enable shadevpn-admin", "enable service")
    run_cmd(ssh, "systemctl restart shadevpn-admin", "restart service")
    print("  Waiting 4 seconds for startup...")
    time.sleep(4)

    # 7. Verify
    print("\n[7/7] Verifying...")
    run_cmd(ssh, "systemctl status shadevpn-admin --no-pager -l 2>&1 | head -15", "Service status")
    health_out, _ = run_cmd(ssh, "curl -s http://localhost:8443/api/health 2>/dev/null || echo FAIL", "Health check")
    sys_out, _ = run_cmd(ssh, "curl -s http://localhost:8443/api/system 2>/dev/null || echo FAIL", "System metrics")

    ssh.close()

    print("\n" + "=" * 60)
    if "ok" in health_out:
        print("  *** DEPLOY SUCCESSFUL! ***")
        print(f"  API:    http://{VPS_IP}:8443/api/health")
        print(f"  System: http://{VPS_IP}:8443/api/system")
        print(f"  clients.json: {clients_json}")
        print()
        print("  Next: change API URL in frontend to:")
        print(f"  http://{VPS_IP}:8443/api")
    else:
        print("  *** DEPLOY FAILED ***")
        print("  Check logs:")
        print(f"  ssh root@{VPS_IP} journalctl -u shadevpn-admin -n 30")
    print("=" * 60)


if __name__ == "__main__":
    main()
