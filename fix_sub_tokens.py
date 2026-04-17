import paramiko
import base64
import time
import sys

def connect(ip, pw, timeout=15):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='root', password=pw, timeout=timeout)
    return ssh

# check schema, add sub_token column if missing, then fix everything
script_fix = r"""
import sqlite3, uuid, base64 as b64lib, json

conn = sqlite3.connect("/opt/shadevpn-admin/shadevpn.db")

# Add sub_token column if it doesn't exist
existing = [row[1] for row in conn.execute("PRAGMA table_info(clients)")]
if "sub_token" not in existing:
    conn.execute("ALTER TABLE clients ADD COLUMN sub_token TEXT")
    conn.commit()
    print("ADDED sub_token column")
else:
    print("sub_token column already exists")

# Add Estonia and Finland nodes if not present
if not list(conn.execute("SELECT id FROM nodes WHERE ip_address='150.241.101.56'")):
    conn.execute("INSERT INTO nodes (id, name, location, ip_address, port, is_online) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "Estonia 1G", "Estonia", "150.241.101.56", 443, 1))
    print("Estonia node added")

if not list(conn.execute("SELECT id FROM nodes WHERE ip_address='2.26.91.190'")):
    conn.execute("INSERT INTO nodes (id, name, location, ip_address, port, is_online) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "Finland Power", "Finland", "2.26.91.190", 443, 1))
    print("Finland node added")

conn.commit()

# Give sub_token to ALL clients that don't have one
updated = 0
for row in list(conn.execute("SELECT id, name, psk, sub_token FROM clients")):
    cid, name, psk, sub_token = row
    if not sub_token:
        new_token = str(uuid.uuid4())
        sub_url = "http://185.204.52.135/api/sub/" + new_token
        sub_payload = json.dumps({"sub": sub_url}, separators=(',', ':'))
        sub_b64 = b64lib.urlsafe_b64encode(sub_payload.encode()).rstrip(b'=').decode()
        new_shade = "shade://" + sub_b64
        conn.execute("UPDATE clients SET sub_token=? WHERE id=?", (new_token, cid))
        conn.commit()
        print("CLIENT:" + name + "|TOKEN:" + new_token + "|KEY:" + new_shade)
        updated += 1

if updated == 0:
    # Show all existing clients with their sub_tokens
    for row in conn.execute("SELECT id, name, sub_token FROM clients"):
        cid, name, sub_token = row
        print("CLIENT:" + name + "|TOKEN:" + (sub_token or "NONE"))

print("DONE:" + str(updated) + " updated")
"""

try:
    for attempt in range(3):
        try:
            sys.stdout.write(f"Connecting (attempt {attempt+1})...\n")
            sys.stdout.flush()
            ssh = connect('185.204.52.135', 'qq%+@YHyrk{WFP$9')
            break
        except Exception as e:
            sys.stdout.write(f"  Failed: {e}\n")
            time.sleep(5)
    else:
        sys.stdout.write("Could not connect!\n")
        exit(1)
    
    encoded = base64.b64encode(script_fix.encode()).decode()
    stdin, stdout, stderr = ssh.exec_command(f"echo {encoded} | base64 -d | python3", get_pty=False)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    
    sys.stdout.write(out + "\n")
    if err:
        sys.stdout.write("STDERR: " + err + "\n")
    
    # Restart admin panel
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active shadevpn-admin")
    status = stdout.read().decode().strip()
    sys.stdout.write(f"Admin service status: {status}\n")
    
    if status == "active":
        ssh.exec_command("systemctl restart shadevpn-admin")
        sys.stdout.write("Admin panel restarted\n")
    
    ssh.close()

except Exception as e:
    import traceback
    traceback.print_exc()
