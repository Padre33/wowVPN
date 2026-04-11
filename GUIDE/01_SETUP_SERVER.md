# ShadeVPN — Полное руководство по установке и управлению

> Бренд: **ShadeVPN** | Префикс ключей: `shade://` | Форк AIVPN (MIT)

---

## Содержание
1. [Подготовка VPS](#1-подготовка-vps)
2. [Установка зависимостей](#2-установка-зависимостей)
3. [Сборка ShadeVPN сервера](#3-сборка-shadevpn-сервера)
4. [Настройка и запуск](#4-настройка-и-запуск)
5. [Управление клиентами](#5-управление-клиентами)
6. [Автозапуск (systemd)](#6-автозапуск-systemd)
7. [Тестирование](#7-тестирование)
8. [Ребрендинг: aivpn → shade](#8-ребрендинг)
9. [Админ-панель](#9-админ-панель)
10. [Telegram бот](#10-telegram-бот)
11. [Клиенты (Android/Windows/macOS)](#11-клиенты)
12. [FAQ и решение проблем](#12-faq)

---

## 1. Подготовка VPS

### Требования
- **ОС:** Ubuntu 22.04 LTS (рекомендуется)
- **CPU:** 1 vCPU минимум
- **RAM:** 1 GB минимум
- **Трафик:** 1 TB/мес минимум
- **Порт:** 443/UDP должен быть открыт
- **Локация:** Нидерланды (у тебя уже есть)

### Первое подключение
```bash
# С твоего компьютера:
ssh root@ТВОЙ_IP_СЕРВЕРА

# Если вход по паролю — сразу ставь SSH ключи:
ssh-keygen -t ed25519
ssh-copy-id root@ТВОЙ_IP_СЕРВЕРА
```

### Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

---

## 2. Установка зависимостей

```bash
# Системные пакеты
sudo apt install -y build-essential pkg-config libssl-dev git curl

# Rust (компилятор)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env

# Проверка
rustc --version   # должно быть 1.75+
cargo --version
```

---

## 3. Сборка ShadeVPN сервера

```bash
# Клонируем твой форк
cd /opt
git clone https://github.com/Padre33/wowVPN.git shadevpn
cd shadevpn

# Собираем (занимает 2-5 минут)
cargo build --release

# Проверяем что собралось
ls -la target/release/aivpn-server
ls -la target/release/aivpn-client
# Оба файла должны существовать
```

### Результат сборки:
```
target/release/aivpn-server  — серверный бинарник (~5 MB)
target/release/aivpn-client  — клиентский бинарник (~2.5 MB)
```

---

## 4. Настройка и запуск

### 4.1 Генерация серверного ключа
```bash
sudo mkdir -p /etc/shadevpn
openssl rand 32 | sudo tee /etc/shadevpn/server.key > /dev/null
sudo chmod 600 /etc/shadevpn/server.key
```

### 4.2 Включение IP forwarding
```bash
# Временно (до перезагрузки)
sudo sysctl -w net.ipv4.ip_forward=1

# Постоянно
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 4.3 Настройка NAT
```bash
# Узнай имя сетевого интерфейса:
ip route show default
# Будет что-то типа: default via 10.0.0.1 dev eth0
# Тебе нужно имя после "dev" (например: eth0, ens3, enp1s0)

# Настрой NAT (замени eth0 на СВОЁ):
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE

# Сохранить правила (чтобы после ребута остались):
sudo apt install -y iptables-persistent
sudo netfilter-persistent save
```

### 4.4 Первый запуск (тест)
```bash
sudo /opt/shadevpn/target/release/aivpn-server \
  --listen 0.0.0.0:443 \
  --key-file /etc/shadevpn/server.key \
  --clients-db /etc/shadevpn/clients.json
```

Если видишь:
```
AIVPN Server v0.2.0
Starting server...
Listening on: 0.0.0.0:443
```
**Сервер работает! ✅**

Ctrl+C чтобы остановить.

---

## 5. Управление клиентами

### Добавить нового клиента
```bash
/opt/shadevpn/target/release/aivpn-server \
  --add-client "Имя_клиента" \
  --key-file /etc/shadevpn/server.key \
  --clients-db /etc/shadevpn/clients.json \
  --server-ip ТВОЙ_ПУБЛИЧНЫЙ_IP:443
```

**Результат:**
```
✅ Client 'Имя_клиента' created!
   ID:     a1b2c3d4e5f67890
   VPN IP: 10.0.0.2

══ Connection Key (paste into app) ══

aivpn://eyJpIjoiMTAuMC4wLjIi...
```
> ⚠️ До ребрендинга ключи будут начинаться с `aivpn://`. После — с `shade://`.

### Показать всех клиентов
```bash
/opt/shadevpn/target/release/aivpn-server \
  --list-clients \
  --clients-db /etc/shadevpn/clients.json
```

### Показать одного клиента (с ключом)
```bash
/opt/shadevpn/target/release/aivpn-server \
  --show-client "Имя_клиента" \
  --key-file /etc/shadevpn/server.key \
  --clients-db /etc/shadevpn/clients.json \
  --server-ip ТВОЙ_ПУБЛИЧНЫЙ_IP:443
```

### Удалить клиента
```bash
/opt/shadevpn/target/release/aivpn-server \
  --remove-client "Имя_клиента" \
  --clients-db /etc/shadevpn/clients.json
```

---

## 6. Автозапуск (systemd)

### Создать сервис
```bash
sudo tee /etc/systemd/system/shadevpn.service << 'EOF'
[Unit]
Description=ShadeVPN Server
After=network.target

[Service]
Type=simple
ExecStart=/opt/shadevpn/target/release/aivpn-server \
  --listen 0.0.0.0:443 \
  --key-file /etc/shadevpn/server.key \
  --clients-db /etc/shadevpn/clients.json
Restart=always
RestartSec=5
LimitNOFILE=65535
Environment=RUST_LOG=info

[Install]
WantedBy=multi-user.target
EOF
```

### Запуск и управление
```bash
# Включить автозапуск
sudo systemctl daemon-reload
sudo systemctl enable shadevpn
sudo systemctl start shadevpn

# Проверить статус
sudo systemctl status shadevpn

# Посмотреть логи
sudo journalctl -u shadevpn -f

# Перезапустить
sudo systemctl restart shadevpn

# Остановить
sudo systemctl stop shadevpn
```

---

## 7. Тестирование

### 7.1 Создать тестового клиента
```bash
/opt/shadevpn/target/release/aivpn-server \
  --add-client "test_admin" \
  --key-file /etc/shadevpn/server.key \
  --clients-db /etc/shadevpn/clients.json \
  --server-ip ТВОЙ_IP:443
```

### 7.2 Подключиться с Windows
```powershell
# Скачай aivpn-client.exe + wintun.dll из releases/
# Запусти PowerShell от Администратора:
.\aivpn-client.exe -k "aivpn://ТВОЙ_КЛЮЧ_СЮДА"
```

### 7.3 Подключиться с Android
1. Скачай `releases/aivpn-client.apk` на телефон
2. Установи (разрешить установку из неизвестных источников)
3. Вставь ключ `aivpn://...`
4. Нажми Connect

### 7.4 Проверки после подключения
```
✅ Открой https://whatismyip.com — IP должен быть сервера (Нидерланды)
✅ Открой https://dnsleaktest.com — DNS не должен утекать
✅ Открой https://fast.com — проверь скорость
✅ Открой любой сайт — должно работать
```

---

## 8. Ребрендинг (aivpn → shade)

### Файлы которые нужно изменить:

#### Сервер (Rust) — главный файл
```
aivpn-server/src/main.rs
  Строка 141: format!("aivpn://{}", encoded)  →  format!("shade://{}", encoded)
  Строка 337: .strip_prefix("aivpn://")  →  .strip_prefix("shade://")
  Строка 53:  "AIVPN Server"  →  "ShadeVPN Server"
  Строка 223: "aivpn-server"  →  "shade-server"
```

#### Клиент CLI (Rust)
```
aivpn-client/src/main.rs
  Строка 75: .strip_prefix("aivpn://")  →  .strip_prefix("shade://")
  Строка 26: "aivpn://"  →  "shade://"
```

#### Windows клиент (Rust)
```
aivpn-windows/src/key_storage.rs
  Строка 20: .strip_prefix("aivpn://")  →  .strip_prefix("shade://")
aivpn-windows/src/localization.rs
  Строка 85-86: "aivpn://"  →  "shade://"
aivpn-windows/src/ui.rs
  Строка 324: "aivpn://..."  →  "shade://..."
```

#### macOS клиент (Swift)
```
aivpn-macos/ConnectionKey.swift — все "aivpn://" → "shade://"
aivpn-macos/LocalizationManager.swift — тексты
aivpn-macos/VPNManager.swift — "aivpn://" → "shade://"
aivpn-macos/ContentView.swift — подсказки
```

#### Android клиент (Kotlin)
```
aivpn-android/app/src/main/java/com/aivpn/client/MainActivity.kt
  Строка 375: "aivpn://" → "shade://"
aivpn-android/app/src/main/res/values/strings.xml
  "aivpn://…" → "shade://…"
aivpn-android/app/src/main/res/values-ru/strings.xml
  "aivpn://…" → "shade://…"
```

#### Cargo.toml
```
authors = ["AIVPN Team"]  →  authors = ["ShadeVPN"]
```

#### README файлы
```
README.md — все "aivpn://" → "shade://"
README_RU.md — все "aivpn://" → "shade://"
```

> ⚠️ ВАЖНО: После ребрендинга нужно пересобрать сервер и ВСЕ клиенты!
> Старые клиенты с "aivpn://" НЕ будут работать с новым сервером.

---

## 9. Админ-панель

Администрирование через Web-интерфейс. Будет создана отдельным проектом.

**Технологии:** Python FastAPI + HTML/CSS/JS
**Порт:** 8443 (HTTPS)
**Функции:**
- Логин с паролем
- Дашборд (статус сервера, онлайн клиенты)
- Управление клиентами (добавить/удалить/список)
- Генерация ключей (одной кнопкой)
- Статистика трафика
- API для Telegram бота

---

## 10. Telegram бот

**Функции:**
- `/start` — приветствие + тарифы
- `/buy` — купить подписку (крипта / TG Stars)
- `/key` — получить свой ключ
- `/help` — инструкция по подключению
- `/status` — статус серверов

**Оплата:** CryptoBot (USDT/TON) + Telegram Stars

---

## 11. Клиенты

### Приоритет разработки:
1. ✅ Windows — есть готовый (CLI + GUI)
2. ✅ Android — есть готовый APK
3. ✅ macOS — есть готовый DMG
4. ⬜ iOS — TestFlight позже

### После ребрендинга нужно:
- Переименовать папки aivpn-* → shade-*
- Поменять applicationId в Android (com.aivpn.client → com.shadevpn.app)
- Поменять иконки и цвета
- Пересобрать все клиенты

---

## 12. FAQ и решение проблем

### Порт 443 занят
```bash
sudo lsof -i :443
# Если занят nginx/apache → остановить или сменить порт на 8443
```

### Клиент не подключается
```bash
# На сервере проверь:
sudo systemctl status shadevpn     # сервер запущен?
sudo ss -ulnp | grep 443           # порт слушается?
sudo iptables -t nat -L            # NAT настроен?
```

### Нет интернета через VPN
```bash
# Проверь IP forwarding:
cat /proc/sys/net/ipv4/ip_forward  # должно быть 1

# Проверь NAT:
sudo iptables -t nat -L POSTROUTING
# Должна быть строка: MASQUERADE ... source 10.0.0.0/24
```

### Как обновить сервер
```bash
cd /opt/shadevpn
git pull
cargo build --release
sudo systemctl restart shadevpn
```
