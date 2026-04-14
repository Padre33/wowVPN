import { motion } from "motion/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Search } from "lucide-react";

interface App {
  id: string;
  name: string;
  icon: string;
  enabled: boolean;
}

const mockApps: App[] = [
  { id: "chrome", name: "Chrome", icon: "🌐", enabled: false },
  { id: "telegram", name: "Telegram", icon: "✈️", enabled: true },
  { id: "whatsapp", name: "WhatsApp", icon: "💬", enabled: false },
  { id: "instagram", name: "Instagram", icon: "📷", enabled: true },
  { id: "youtube", name: "YouTube", icon: "📺", enabled: false },
  { id: "spotify", name: "Spotify", icon: "🎵", enabled: false },
  { id: "netflix", name: "Netflix", icon: "🎬", enabled: false },
  { id: "gmail", name: "Gmail", icon: "📧", enabled: false },
  { id: "maps", name: "Google Maps", icon: "🗺️", enabled: false },
  { id: "twitter", name: "Twitter", icon: "🐦", enabled: false },
];

export function SplitTunnelingScreen() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [apps, setApps] = useState<App[]>(mockApps);

  const filteredApps = apps.filter((app) =>
    app.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const toggleApp = (appId: string) => {
    setApps((prev) =>
      prev.map((app) =>
        app.id === appId ? { ...app, enabled: !app.enabled } : app
      )
    );
  };

  return (
    <div className="min-h-screen w-full bg-[#0D0F14] flex flex-col">
      {/* Header */}
      <div className="p-6 space-y-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/settings")}
            className="p-2 hover:bg-[#1A1D26] rounded-lg transition-colors"
          >
            <ArrowLeft className="text-[#F0F2F5]" size={24} />
          </button>
          <div>
            <h1 className="text-2xl font-semibold text-[#F0F2F5]">
              Выберите приложения
            </h1>
            <p className="text-[#8B8F9A] text-sm">
              Эти приложения будут работать в обход VPN
            </p>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search
            className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8B8F9A]"
            size={18}
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Поиск приложений..."
            className="w-full bg-[#252830] text-[#F0F2F5] pl-12 pr-4 py-3 rounded-xl border-2 border-transparent focus:border-[#00E5FF] focus:shadow-[0_0_20px_rgba(0,229,255,0.2)] transition-all outline-none"
          />
        </div>
      </div>

      {/* App list */}
      <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-2">
        {filteredApps.map((app, index) => (
          <motion.div
            key={app.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.03 }}
            className="bg-[#1A1D26] rounded-xl p-4 flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#252830] rounded-xl flex items-center justify-center text-2xl">
                {app.icon}
              </div>
              <p className="text-[#F0F2F5] font-medium">{app.name}</p>
            </div>
            <button
              onClick={() => toggleApp(app.id)}
              className={`relative w-14 h-8 rounded-full transition-all ${
                app.enabled ? "bg-[#00E5FF]" : "bg-[#252830]"
              }`}
            >
              <motion.div
                className="absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg"
                animate={{ x: app.enabled ? 30 : 4 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            </button>
          </motion.div>
        ))}
      </div>

      {/* Info footer */}
      <div className="p-6 pt-0">
        <div className="bg-[#1A1D26] rounded-xl p-4 border border-[#00E5FF]/30">
          <p className="text-[#8B8F9A] text-sm text-center">
            Включенные приложения будут обходить VPN и использовать прямое
            подключение к интернету
          </p>
        </div>
      </div>
    </div>
  );
}
