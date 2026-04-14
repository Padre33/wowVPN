#!/bin/bash
# ═══════════════════════════════════════════════════════
#  ShadeVPN Admin Backend — Deploy to VPS
#  Запускать с Windows: scp + ssh через PowerShell
#  Или просто скопируй файлы на сервер вручную
# ═══════════════════════════════════════════════════════

VPS_IP="185.204.52.135"
VPS_USER="root"
REMOTE_DIR="/opt/shadevpn-admin"

echo "═══ ShadeVPN Admin Deploy ═══"

# 1. Создать директорию на сервере
ssh ${VPS_USER}@${VPS_IP} "mkdir -p ${REMOTE_DIR}"

# 2. Скопировать бэкенд
scp -r main.py database.py sync.py requirements.txt ${VPS_USER}@${VPS_IP}:${REMOTE_DIR}/

# 3. Установить зависимости и запустить
ssh ${VPS_USER}@${VPS_IP} << 'EOF'
cd /opt/shadevpn-admin

# Установить Python если нет
apt-get update && apt-get install -y python3 python3-pip python3-venv

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настроить путь к clients.json (где Rust-ядро хранит данные)
export AIVPN_CLIENTS_JSON="/etc/aivpn/clients.json"

# Создать systemd сервис
cat > /etc/systemd/system/shadevpn-admin.service << 'SERVICE'
[Unit]
Description=ShadeVPN Admin Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/shadevpn-admin
Environment="AIVPN_CLIENTS_JSON=/etc/aivpn/clients.json"
ExecStart=/opt/shadevpn-admin/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8443
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

# Перезапустить
systemctl daemon-reload
systemctl enable shadevpn-admin
systemctl restart shadevpn-admin

echo "✅ ShadeVPN Admin Backend deployed and running!"
echo "   API: http://${HOSTNAME}:8443/api/health"
EOF

echo "═══ Deploy complete! ═══"
echo "Теперь в frontend поменяй API URL на: http://${VPS_IP}:8443/api"
