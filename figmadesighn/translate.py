import os
import re

DIRECTORY = r"C:\Users\user\Desktop\contract checker\wowVPN_repo\figmadesighn\src\app\pages"

TRANSLATIONS = {
    # Nodes.tsx
    r'>Nodes<': '>Серверы<',
    r'Manage VPN server nodes and their status': 'Управление серверами VPN и их статусами',
    r'>Add Node<': '>Добавить сервер<',
    r'LOCATION': 'ЛОКАЦИЯ',
    r'IP ADDRESS': 'IP АДРЕС',
    r'LOAD': 'НАГРУЗКА',
    r'Delete Selected': 'Удалить выбранные',
    r'>Edit Node<': '>Редактировать сервер<',

    # Templates.tsx
    r'>Templates<': '>Тарифы<',
    r'Manage subscription templates and data limits': 'Управление шаблонами тарифов и лимитами трафика',
    r'>Add Template<': '>Создать тариф<',
    r'TEMPLATE NAME': 'НАЗВАНИЕ ТАРИФА',
    r'DURATION': 'ДЛИТЕЛЬНОСТЬ',
    r'DATA LIMIT': 'ЛИМИТ ТРАФИКА',
    r'PRICE': 'ЦЕНА',

    # ConnectionLogs.tsx
    r'>Connection Logs<': '>Логи подключений<',
    r'View real-time connection events and history': 'История подключений клиентов в реальном времени',
    r'>Export Logs<': '>Экспорт логов<',
    r'TIME': 'ВРЕМЯ',
    r'USER': 'КЛИЕНТ',
    r'EVENT': 'СОБЫТИЕ',
    r'IP / LOCATION': 'IP / ЛОКАЦИЯ',
    r'DETAILS': 'ДЕТАЛИ',

    # Settings.tsx
    r'>Settings<': '>Настройки<',
    r'Configure panel and server global settings': 'Глобальные настройки панели и серверов',
    r'>Save Settings<': '>Сохранить настройки<',
    r'>Global Settings<': '>Глобальные настройки<',

    # Common buttons across all pages
    r'>Cancel<': '>Отмена<',
    r'Save Changes': 'Сохранить изменения',
    r'ACTIONS': 'ДЕЙСТВИЯ',
    r'STATUS': 'СТАТУС',
    r'active': 'Активен',
    r'offline': 'Не в сети',
    r'online': 'В сети'
}

for root, _, files in os.walk(DIRECTORY):
    for file in files:
        if file.endswith(".tsx") and file not in ["Home.tsx", "Users.tsx"]: 
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for eng, rus in TRANSLATIONS.items():
                content = re.sub(eng, rus, content, flags=re.IGNORECASE)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
print("Translating remaining UI pages complete!")
