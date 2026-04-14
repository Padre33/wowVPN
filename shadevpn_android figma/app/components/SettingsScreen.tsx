import { motion } from "motion/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ChevronRight,
  Shield,
  ShieldOff,
  Globe,
  Palette,
  Key,
  UserPlus,
  MessageSquare,
  Info,
} from "lucide-react";

export function SettingsScreen() {
  const navigate = useNavigate();
  const [killSwitch, setKillSwitch] = useState(true);
  const [netShield, setNetShield] = useState(true);
  const [language, setLanguage] = useState("Русский");
  const [theme, setTheme] = useState<"light" | "dark" | "system">("dark");

  const handleChangeKey = () => {
    localStorage.removeItem("shadeVPN_key");
    navigate("/onboarding", { replace: true });
  };

  const handleInvite = () => {
    alert("Открывается реферальная ссылка в Telegram-бот");
  };

  const handleFeedback = () => {
    alert("Форма обратной связи будет отправлена в Telegram-бот");
  };

  return (
    <div className="min-h-screen w-full bg-[#0D0F14] flex flex-col">
      {/* Header */}
      <div className="p-6">
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => navigate("/home")}
            className="p-2 hover:bg-[#1A1D26] rounded-lg transition-colors"
          >
            <ArrowLeft className="text-[#F0F2F5]" size={24} />
          </button>
          <h1 className="text-2xl font-semibold text-[#F0F2F5]">Настройки</h1>
        </div>
      </div>

      {/* Settings sections */}
      <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-6">
        {/* Connection section */}
        <div className="space-y-3">
          <h2 className="text-[#8B8F9A] text-sm font-semibold uppercase tracking-wider">
            Соединение
          </h2>

          {/* Kill Switch */}
          <div className="bg-[#1A1D26] rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="text-[#00E5FF]" size={20} />
              <div>
                <p className="text-[#F0F2F5] font-medium">Kill Switch</p>
                <p className="text-[#8B8F9A] text-sm">
                  Блокировать интернет при обрыве VPN
                </p>
              </div>
            </div>
            <button
              onClick={() => setKillSwitch(!killSwitch)}
              className={`relative w-14 h-8 rounded-full transition-all ${
                killSwitch ? "bg-[#00E5FF]" : "bg-[#252830]"
              }`}
            >
              <motion.div
                className="absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg"
                animate={{ x: killSwitch ? 30 : 4 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            </button>
          </div>

          {/* NetShield */}
          <div className="bg-[#1A1D26] rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ShieldOff className="text-[#00E5FF]" size={20} />
              <div>
                <p className="text-[#F0F2F5] font-medium">NetShield</p>
                <p className="text-[#8B8F9A] text-sm">
                  Блокировка рекламы и трекеров
                </p>
              </div>
            </div>
            <button
              onClick={() => setNetShield(!netShield)}
              className={`relative w-14 h-8 rounded-full transition-all ${
                netShield ? "bg-[#00E5FF]" : "bg-[#252830]"
              }`}
            >
              <motion.div
                className="absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg"
                animate={{ x: netShield ? 30 : 4 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            </button>
          </div>

          {/* Split Tunneling */}
          <button
            onClick={() => navigate("/split-tunneling")}
            className="w-full bg-[#1A1D26] hover:bg-[#252830] rounded-xl p-4 flex items-center justify-between transition-all"
          >
            <div className="flex items-center gap-3">
              <Globe className="text-[#00E5FF]" size={20} />
              <div className="text-left">
                <p className="text-[#F0F2F5] font-medium">
                  Split Tunneling
                </p>
                <p className="text-[#8B8F9A] text-sm">
                  Раздельное туннелирование
                </p>
              </div>
            </div>
            <ChevronRight className="text-[#8B8F9A]" size={20} />
          </button>
        </div>

        {/* Interface section */}
        <div className="space-y-3">
          <h2 className="text-[#8B8F9A] text-sm font-semibold uppercase tracking-wider">
            Интерфейс
          </h2>

          {/* Language */}
          <button
            onClick={() => {
              const langs = ["Русский", "English", "Deutsch"];
              const currentIndex = langs.indexOf(language);
              setLanguage(langs[(currentIndex + 1) % langs.length]);
            }}
            className="w-full bg-[#1A1D26] hover:bg-[#252830] rounded-xl p-4 flex items-center justify-between transition-all"
          >
            <div className="flex items-center gap-3">
              <Globe className="text-[#00E5FF]" size={20} />
              <p className="text-[#F0F2F5] font-medium">Язык</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[#8B8F9A]">{language}</span>
              <ChevronRight className="text-[#8B8F9A]" size={20} />
            </div>
          </button>

          {/* Theme */}
          <div className="bg-[#1A1D26] rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <Palette className="text-[#00E5FF]" size={20} />
              <p className="text-[#F0F2F5] font-medium">Тема оформления</p>
            </div>
            <div className="flex gap-2">
              {(["light", "dark", "system"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                    theme === t
                      ? "bg-[#00E5FF] text-[#0D0F14]"
                      : "bg-[#252830] text-[#8B8F9A] hover:text-[#F0F2F5]"
                  }`}
                >
                  {t === "light" ? "Светлая" : t === "dark" ? "Тёмная" : "Системная"}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Account section */}
        <div className="space-y-3">
          <h2 className="text-[#8B8F9A] text-sm font-semibold uppercase tracking-wider">
            Аккаунт
          </h2>

          {/* Current key */}
          <div className="bg-[#1A1D26] rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <Key className="text-[#00E5FF]" size={20} />
              <div className="flex-1">
                <p className="text-[#F0F2F5] font-medium">Текущий ключ</p>
                <p className="text-[#8B8F9A] text-xs font-mono">
                  shade://eyJ...7a3F
                </p>
              </div>
            </div>
            <button
              onClick={handleChangeKey}
              className="w-full py-2 bg-[#252830] hover:bg-[#FF3D57] text-[#F0F2F5] rounded-lg transition-all text-sm font-medium"
            >
              Сменить ключ
            </button>
          </div>

          {/* Invite */}
          <button
            onClick={handleInvite}
            className="w-full bg-[#1A1D26] hover:bg-[#252830] rounded-xl p-4 flex items-center justify-between transition-all"
          >
            <div className="flex items-center gap-3">
              <UserPlus className="text-[#00E5FF]" size={20} />
              <p className="text-[#F0F2F5] font-medium">Пригласить друга</p>
            </div>
            <ChevronRight className="text-[#8B8F9A]" size={20} />
          </button>
        </div>

        {/* Support section */}
        <div className="space-y-3">
          <h2 className="text-[#8B8F9A] text-sm font-semibold uppercase tracking-wider">
            Поддержка
          </h2>

          {/* Feedback */}
          <button
            onClick={handleFeedback}
            className="w-full bg-[#1A1D26] hover:bg-[#252830] rounded-xl p-4 flex items-center justify-between transition-all"
          >
            <div className="flex items-center gap-3">
              <MessageSquare className="text-[#00E5FF]" size={20} />
              <p className="text-[#F0F2F5] font-medium">
                Помогите нам стать лучше
              </p>
            </div>
            <ChevronRight className="text-[#8B8F9A]" size={20} />
          </button>

          {/* About */}
          <button className="w-full bg-[#1A1D26] hover:bg-[#252830] rounded-xl p-4 flex items-center justify-between transition-all">
            <div className="flex items-center gap-3">
              <Info className="text-[#00E5FF]" size={20} />
              <div className="text-left">
                <p className="text-[#F0F2F5] font-medium">О приложении</p>
                <p className="text-[#8B8F9A] text-xs">Версия 1.0.0</p>
              </div>
            </div>
            <ChevronRight className="text-[#8B8F9A]" size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
