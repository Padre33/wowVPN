#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  ShadeVPN Admin Panel — One-Click Deploy Script
#  Запускай на сервере: bash /opt/shadevpn/deploy_admin.sh
# ═══════════════════════════════════════════════════════════

set -e  # Остановиться при первой ошибке

echo "══════════════════════════════════════════════"
echo "  🚀 ShadeVPN Admin Panel — Развертывание"
echo "══════════════════════════════════════════════"

# 1. Обновляем код из GitHub
echo ""
echo "📥 Шаг 1/6: Скачиваем свежий код из GitHub..."
cd /opt/shadevpn
git pull origin master

# 2. Устанавливаем Python-зависимости
echo ""
echo "🐍 Шаг 2/6: Настраиваем Python-окружение..."
cd /opt/shadevpn/shadevpn-admin-backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --quiet -r requirements.txt

# 3. Создаём службу для Python-бэкенда
echo ""
echo "⚙️  Шаг 3/6: Создаём фоновую службу для API бэкенда..."
cat > /etc/systemd/system/shadevpn-admin.service << 'SERVICEEOF'
[Unit]
Description=ShadeVPN Admin FastAPI Backend
After=network.target shadevpn.service

[Service]
User=root
WorkingDirectory=/opt/shadevpn/shadevpn-admin-backend
Environment="PATH=/opt/shadevpn/shadevpn-admin-backend/venv/bin"
ExecStart=/opt/shadevpn/shadevpn-admin-backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable shadevpn-admin
systemctl restart shadevpn-admin

# 4. Устанавливаем и настраиваем Nginx
echo ""
echo "🌐 Шаг 4/6: Устанавливаем веб-сервер Nginx..."
apt install -y nginx > /dev/null 2>&1

# 5. Создаём конфигурацию Nginx
echo ""
echo "📄 Шаг 5/6: Настраиваем маршрутизацию Nginx..."
cat > /etc/nginx/sites-available/shadevpn-admin << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    # Фронтенд (красивый дизайн панели)
    root /opt/shadevpn/figmadesighn/dist;
    index index.html;

    # Все API запросы перенаправляем на Python-бэкенд
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Для всех остальных путей — отдаём index.html (React SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }
}
NGINXEOF

# Активируем наш сайт, убираем дефолтный
ln -sf /etc/nginx/sites-available/shadevpn-admin /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверяем конфиг и перезапускаем
nginx -t
systemctl restart nginx
systemctl enable nginx

# 6. Открываем порт 80 в фаерволе (если UFW активен)
echo ""
echo "🔓 Шаг 6/6: Открываем порт 80..."
ufw allow 80/tcp > /dev/null 2>&1 || true

echo ""
echo "══════════════════════════════════════════════"
echo "  ✅ ГОТОВО! Админ-панель развернута!"
echo ""
echo "  Открой в браузере: http://185.204.52.135"
echo ""
echo "  Проверка статуса:"
echo "    systemctl status shadevpn-admin"
echo "    systemctl status nginx"
echo "══════════════════════════════════════════════"
