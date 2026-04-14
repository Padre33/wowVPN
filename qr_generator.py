import json
import base64
import qrcode
import os

print("--- Генератор ключей и QR-кодов для ShadeVPN ---")

# Основные данные сервера (одинаковые для всех клиентов)
server_addr = input("Введите IP и порт сервера (например, 185.0.0.1:443): ").strip()
server_key = input("Введите публичный ключ сервера (base64): ").strip()
psk = input("Введите PSK (если нет, оставьте пустым): ").strip()

clients_count = int(input("Сколько клиентов нужно создать? (Например: 3): ").strip())

for i in range(1, clients_count + 1):
    print(f"\n--- Клиент {i} ---")
    client_ip = input(f"Введите локальный VPN IP для клиента {i} (например, 10.0.0.{i+1}): ").strip()
    
    # Формируем JSON
    payload_dict = {
        "s": server_addr,
        "k": server_key,
        "p": psk,
        "i": client_ip
    }
    
    # Преобразуем в компактный JSON без пробелов
    json_str = json.dumps(payload_dict, separators=(',', ':'))
    
    # Кодируем в URL-safe Base64 (без padding)
    b64_bytes = base64.urlsafe_b64encode(json_str.encode('utf-8'))
    b64_str = b64_bytes.decode('utf-8').rstrip('=')
    
    # Итоговый линк
    final_link = f"shade://{b64_str}"
    print(f"Ключ для Клиента {i}:")
    print(final_link)
    
    # Генерируем QR
    img = qrcode.make(final_link)
    filename = f"Client_{i}_{client_ip}.png"
    img.save(filename)
    print(f"✅ QR-код сохранен как {filename} в текущей папке.")

print("\nГотово! Файлы QR-кодов лежат рядом со скриптом.")
