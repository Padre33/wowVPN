import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "shadevpn.db")

data = {
    "Мер тест": "shade://eyJpIjoiMTAuMC4wLjE1IiwiayI6ImdIbHJLanNRUHlVbGVJY2lFQVQ0WGxSVUVwSjY3Q2lyZUtkUHNZTUk0aVU9IiwicCI6ImxpajlaWFh5eW53Z1VRM1RDTk1OMVpkSlhLN3lqMTlTQWR3QUdDakFPVzQ9IiwicyI6IjE4NS4yMDQuNTIuMTM1OjQ0MyJ9",
    "Пупок": "shade://eyJpIjoiMTAuMC4wLjE3IiwiayI6ImdIbHJLanNRUHlVbGVJY2lFQVQ0WGxSVUVwSjY3Q2lyZUtkUHNZTUk0aVU9IiwicCI6IjEzVlJUbmhmRFFQYTdDQmxoMjFRK3YxZEU5aDkrZ2R4RURjNW4xR1FoSms9IiwicyI6IjE4NS4yMDQuNTIuMTM1OjQ0MyJ9"
}

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    count = 0
    for name, psk in data.items():
        cur.execute("UPDATE clients SET psk=? WHERE name=?", (psk, name))
        if cur.rowcount > 0:
            count += 1
            print(f"✅ Обновлен ключ для: {name}")
        else:
            print(f"⚠️ Клиент не найден в БД: {name}")
    conn.commit()
    conn.close()
    print(f"Успешно обновлено {count} клиентов!")
except Exception as e:
    print(f"Ошибка: {e}")
