import paramiko, base64, time, sys

REAL_DB = "/opt/shadevpn/shadevpn-admin-backend/shadevpn.db"

script = r"""
import sqlite3, uuid, json, base64 as b64lib
import sys

DB = "/opt/shadevpn/shadevpn-admin-backend/shadevpn.db"
conn = sqlite3.connect(DB)

# Show schema
cols = [row[1] for row in conn.execute("PRAGMA table_info(clients)")]
print("CLIENT COLS:", cols)

# Add sub_token column if missing
if "sub_token" not in cols:
    conn.execute("ALTER TABLE clients ADD COLUMN sub_token TEXT")
    conn.commit()
    print("ADDED sub_token")

# Show clients
print("\nCLIENTS before fix:")
for row in conn.execute("SELECT id, name, sub_token FROM clients"):
    print(" ", row)

# Fix sub_tokens
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
        print("FIXED " + name + " token=" + new_token + " key=" + new_shade)
        updated += 1

# Check nodes table columns
node_cols = [row[1] for row in conn.execute("PRAGMA table_info(nodes)")]
print("\nNODE COLS:", node_cols)

# Add nodes if not present
if not list(conn.execute("SELECT id FROM nodes WHERE ip_address='150.241.101.56'")):
    conn.execute("INSERT INTO nodes (id, name, location, ip_address, port, is_online) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "Estonia 1G", "Estonia", "150.241.101.56", 443, 1))
    conn.commit()
    print("Estonia added")

if not list(conn.execute("SELECT id FROM nodes WHERE ip_address='2.26.91.190'")):
    conn.execute("INSERT INTO nodes (id, name, location, ip_address, port, is_online) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), "Finland Power", "Finland", "2.26.91.190", 443, 1))
    conn.commit()
    print("Finland added")

print("\nNODES:")
for row in conn.execute("SELECT name, ip_address FROM nodes"):
    print(" ", row)

print("\nSHOWING FINAL KEYS:")
for row in conn.execute("SELECT name, sub_token FROM clients"):
    name, token = row
    if token:
        sub_url = "http://185.204.52.135/api/sub/" + token
        sub_payload = json.dumps({"sub": sub_url}, separators=(',', ':'))
        sub_b64 = b64lib.urlsafe_b64encode(sub_payload.encode()).rstrip(b'=').decode()
        shade = "shade://" + sub_b64
        print(name + ": " + shade)
    else:
        print(name + ": NO SUBTOKEN!")

print("DONE updated=" + str(updated))
"""

def connect():
    for i in range(5):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('185.204.52.135', username='root', password='qq%+@YHyrk{WFP$9', timeout=10)
            return ssh
        except Exception as e:
            print(f"Connect fail {i+1}: {e}")
            time.sleep(10)
    raise Exception("Failed to connect")

ssh = connect()
encoded = base64.b64encode(script.encode()).decode()
stdin, stdout, stderr = ssh.exec_command(f"echo {encoded} | base64 -d | python3", timeout=30)
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(out)
if err:
    print("ERR:", err[:1000])

# Restart admin so it reloads the DB
ssh.exec_command("systemctl restart shadevpn-admin")
print("Admin panel restarted!")
ssh.close()
