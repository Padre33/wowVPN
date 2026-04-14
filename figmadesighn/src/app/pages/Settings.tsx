import { useState, useEffect, useRef } from "react";
import { Save, Database, Send, Lock, Download, Upload, Server } from "lucide-react";
import { API } from "../config";

export function Settings() {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState("");

  // Refs for all inputs
  const portRef = useRef<HTMLInputElement>(null);
  const stealthRef = useRef<HTMLInputElement>(null);
  const loggingRef = useRef<HTMLInputElement>(null);
  const botTokenRef = useRef<HTMLInputElement>(null);
  const chatIdRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch(`${API}/settings`)
      .then(r => r.json())
      .then(data => setSettings(data))
      .catch(() => {});
  }, []);

  const saveSection = async (data: Record<string, string>) => {
    await fetch(`${API}/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ settings: data }),
    });
    setSaved("✅ Сохранено!");
    setTimeout(() => setSaved(""), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold">Настройки</h1>
        <p className="text-muted-foreground mt-1">
          Конфигурация системы и предпочтения
        </p>
        {saved && (
          <p className="text-sm text-green-400 mt-2 animate-pulse">{saved}</p>
        )}
      </div>

      {/* Резервное копирование */}
      <section className="p-6 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-lg bg-primary/10">
            <Database className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Резервное копирование</h2>
            <p className="text-sm text-muted-foreground">
              Управление бекапами базы данных
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
            <div>
              <p className="font-medium">Скачать бекап</p>
              <p className="text-sm text-muted-foreground">
                Скачать текущую базу данных shadevpn.db
              </p>
            </div>
            <a
              href={`${API}/backup/download`}
              download
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Download className="w-4 h-4" />
              Скачать бекап
            </a>
          </div>
        </div>
      </section>

      {/* Telegram Bot Integration */}
      <section className="p-6 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-lg bg-primary/10">
            <Send className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Интеграция Telegram Бота</h2>
            <p className="text-sm text-muted-foreground">
              Настройка бота для уведомлений и авто-продаж
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Токен Бота (Bot Token)</label>
            <input
              ref={botTokenRef}
              type="password"
              className="w-full px-4 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
              placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
              defaultValue={settings.telegram_bot_token || ""}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Твой ID чата (Admin Chat ID)
            </label>
            <input
              ref={chatIdRef}
              type="text"
              className="w-full px-4 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
              placeholder="123456789"
              defaultValue={settings.telegram_admin_chat_id || ""}
            />
          </div>

          <button
            onClick={() =>
              saveSection({
                telegram_bot_token: botTokenRef.current?.value || "",
                telegram_admin_chat_id: chatIdRef.current?.value || "",
              })
            }
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Save className="w-4 h-4" />
            Сохранить настройки бота
          </button>
        </div>
      </section>

      {/* VPN Config */}
      <section className="p-6 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-lg bg-primary/10">
            <Server className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-bold">VPN Конфигуратор</h2>
            <p className="text-sm text-muted-foreground">
              Управление портами и маскировкой ShadeVPN сервера
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Порт сервера (Server Port)</label>
            <input
              ref={portRef}
              type="number"
              className="w-full px-4 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
              placeholder="443"
              defaultValue={settings.server_port || "443"}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Маскировка трафика (Stealth Domain)
            </label>
            <input
              ref={stealthRef}
              type="text"
              className="w-full px-4 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
              placeholder="www.microsoft.com"
              defaultValue={settings.stealth_domain || "www.apple.com"}
            />
            <p className="text-xs text-muted-foreground mt-1">Внешний домен для обхода DPI (Deep Packet Inspection)</p>
          </div>

          <div className="flex items-center gap-3 py-2">
            <input
              ref={loggingRef}
              type="checkbox"
              id="logging"
              className="w-4 h-4 rounded border-border"
              defaultChecked={settings.logging_enabled !== "false"}
            />
            <label htmlFor="logging" className="text-sm font-medium">Включить продвинутое логирование подключений</label>
          </div>

          <button
            onClick={() =>
              saveSection({
                server_port: portRef.current?.value || "443",
                stealth_domain: stealthRef.current?.value || "",
                logging_enabled: loggingRef.current?.checked ? "true" : "false",
              })
            }
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Save className="w-4 h-4" />
            Сохранить настройки сервера
          </button>
        </div>
      </section>

      {/* Security */}
      <section className="p-6 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-lg bg-primary/10">
            <Lock className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Безопасность</h2>
            <p className="text-sm text-muted-foreground">
              Настройки паролей и авторизации
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Текущий пароль</label>
            <input
              type="password"
              className="w-full px-4 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
              placeholder="Введите текущий пароль"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Новый пароль</label>
            <input
              type="password"
              className="w-full px-4 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
              placeholder="Введите новый пароль"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Подтверждение пароля</label>
            <input
              type="password"
              className="w-full px-4 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
              placeholder="Подтвердите новый пароль"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
            <Lock className="w-4 h-4" />
            Обновить пароль
          </button>
        </div>
      </section>
    </div>
  );
}
