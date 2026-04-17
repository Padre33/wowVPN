import sqlite3

db = sqlite3.connect(r'C:\Users\user\Desktop\contract checker\wowVPN_repo\shadevpn-admin-backend\shadevpn.db')
cursor = db.cursor()
cursor.execute("SELECT id, name, location, ip_address FROM nodes")
rows = cursor.fetchall()
for r in rows:
    print(r)
