import os
import re

DIRECTORY = r"C:\Users\user\Desktop\contract checker\wowVPN_repo\figmadesighn\src\app\pages"

FIXES = {
    r'КЛИЕНТs as КЛИЕНТsIcon': 'Users as UsersIcon',
    r'<КЛИЕНТsIcon': '<UsersIcon',
    r'100 GB/КЛИЕНТ': '100 ГБ/юзер',
    r'25 GB/КЛИЕНТ': '25 ГБ/юзер',
    r'0 GB/КЛИЕНТ': '0 ГБ/юзер',
    r'Organize КЛИЕНТs into categories': 'Организация клиентов по категориям',
    r'Organize users into categories': 'Организация клиентов по категориям',
    r'>Create Group<': '>Создать группу<',
    r'>Create Rule<': '>Создать правило<',
    r'>New Template<': '>Новый тариф<',
    
    r'КЛИЕНТ account created': 'Новый аккаунт создан',
    r'New КЛИЕНТ Welcome': 'Приветствие нового клиента',
    r'КЛИЕНТNAME': 'ИМЯ КЛИЕНТА',
    r'КЛИЕНТ_premium_001': 'user_premium_001',
    r'КЛИЕНТ_suspicious_042': 'user_suspicious_042',
    r'КЛИЕНТ_family_vip': 'user_family_vip',
    r'КЛИЕНТ_shared_key': 'user_shared_key',
    r'ЛОКАЦИЯS': 'ЛОКАЦИЯ',
}

for root, _, files in os.walk(DIRECTORY):
    for file in files:
        if file.endswith(".tsx"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for bad, good in FIXES.items():
                content = content.replace(bad, good)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
print("Syntax artifacts fixed.")
