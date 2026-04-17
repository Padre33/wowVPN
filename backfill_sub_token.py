import sqlite3
import uuid
db = sqlite3.connect('/opt/shadevpn/shadevpn-admin-backend/shadevpn.db')
c = db.cursor()
c.execute("SELECT id FROM clients WHERE sub_token IS NULL OR sub_token = ''")
rows = c.fetchall()
count = 0
for row in rows:
    c_id = row[0]
    sub_token = str(uuid.uuid4())
    c.execute("UPDATE clients SET sub_token = ? WHERE id = ?", (sub_token, c_id))
    print(f"Updated {c_id} with sub_token {sub_token}")
    count += 1
db.commit()
db.close()
print(f"Done, updated {count} rows")
