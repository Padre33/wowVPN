import os
import re

DIRECTORY = r"C:\Users\user\Desktop\contract checker\wowVPN_repo\figmadesighn\src\app\pages"

# Careful dictionary of exact phrases to translate
TRANSLATIONS = {
    # Groups.tsx
    r'>Groups<': '>Группы<',
    r'Organize users into categories': 'Организация клиентов по категориям',
    r'>Create Group<': '>Создать группу<',
    r'Family subscription plan': 'Семейный план подписки',
    r'Premium unlimited access': 'Премиум безлимитный доступ',
    r'Beta testing accounts': 'Аккаунты для бета-тестирования',
    r'Accounts with expired subscriptions': 'Аккаунты с истекшей подпиской',
    r'Members': 'Участников',
    r'Data Limit': 'Лимит Трафика',
    r'100 GB/user': '100 ГБ/юзер',
    r'25 GB/user': '25 ГБ/юзер',
    r'0 GB/user': '0 ГБ/юзер',
    r'>Unlimited<': '>Безлимит<',

    # Templates.tsx
    r'>Subscription Templates<': '>Шаблоны Тарифов<',
    r'Pre-configured subscription plans': 'Предустановленные тарифные планы',
    r'>New Template<': '>Новый Тариф<',
    r'1 Month / 50 GB': '1 Месяц / 50 ГБ',
    r'3 Months / 150 GB': '3 Месяца / 150 ГБ',
    r'VIP Unlimited': 'VIP Безлимит',
    r'Trial / 5 GB': 'Пробный / 5 ГБ',
    r'>Free<': '>Бесплатно<',
    r'30 days': '30 дней',
    r'90 days': '90 дней',
    r'365 days': '365 дней',
    r'7 days': '7 дней',

    # ResponseRules.tsx
    r'>Response Rules<': '>Правила Биллинга<',
    # Fix the weird hybrid phrase that broke earlier:
    r'Automated ДЕЙСТВИЯ based on СОБЫТИЕs': 'Автоматические действия на основе триггеров',
    r'Automated actions based on events': 'Автоматические действия на основе триггеров',
    r'>Create Rule<': '>Создать Правило<',
    r'Traffic 90% Warning': 'Предупреждение: 90% трафика',
    r'Data usage reaches 90%': 'Трафик достигает 90% лимита',
    r'Send Telegram notification': 'Отправить уведомление в Telegram',
    r'Subscription Expired': 'Подписка истёкла',
    r'Subscription end date passed': 'Наступила дата окончания',
    r'Block access \+ move to Expired group': 'Блокировка доступа + перенос в Истёкшие',
    r'New КЛИЕНТ Welcome': 'Приветствие нового клиента',
    r'КЛИЕНТ account created': 'Новый аккаунт создан',
    r'New User Welcome': 'Приветствие нового клиента',
    r'User account created': 'Новый аккаунт создан',
    r'Send welcome message with setup guide': 'Отправить приветствие с инструкцией',
    r'Unusual Activity Detection': 'Подозрительная активность',
    r'Multiple IPs from different countries': 'Несколько IP из разных стран',
    r'Alert admin \+ temporarily suspend': 'Уведомить админа + временный бан',
    r'Trigger:': 'Событие:',
    r'Action:': 'Действие:',

    # HWIDInspector.tsx
    r'>HWID Inspector<': '>Контроль Устройств<',
    r'Device tracking and anti-sharing detection': 'Отслеживание устройств и анти-шаринг',
    r'Total Monitored': 'Всего отслеживается',
    r'Safe Accounts': 'Безопасные аккаунты',
    r'Suspicious Activity': 'Подозрительная активность',
    r'DEVICES': 'УСТРОЙСТВА',
    r'LAST SEEN': 'БЫЛ В СЕТИ',
    r'1 device': '1 устройство',
    r'2 devices': '2 устройства',
    r'3 devices': '3 устройства',
    r'5 devices': '5 устройств',
    r'2h ago': '2ч назад',
    r'15m ago': '15м назад',
    r'1h ago': '1ч назад',
    r'5m ago': '5м назад',

    # Settings.tsx
    r'>Settings<': '>Настройки<',
    r'System configuration and preferences': 'Конфигурация системы и предпочтения',
    r'Backup & Restore': 'Резервное копирование',
    r'Manage database backups and restore points': 'Управление бекапами базы данных',
    r'Last Backup': 'Последний Бекап',
    r'>Download Backup<': '>Скачать Бекап<',
    r'Restore from File': 'Восстановление',
    r'Upload a backup file to restore': 'Загрузить файл бекапа',
    r'>Upload<': '>Загрузить<',
    r'Telegram Bot Integration': 'Интеграция Telegram Бота',
    r'Configure Telegram bot for notifications and billing': 'Настройка бота для уведомлений и авто-продаж',
    r'Bot Token': 'Токен Бота (Bot Token)',
    r'Admin Chat ID': 'Твой ID чата (Admin Chat ID)',
    r'>Save Integration Settings<': '>Сохранить настройки бота<',
    r'Security': 'Безопасность',
}

for root, _, files in os.walk(DIRECTORY):
    for file in files:
        if file.endswith(".tsx"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for eng, rus in TRANSLATIONS.items():
                content = re.sub(eng, rus, content)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

print("Translation fixed globally!")
