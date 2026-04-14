import { motion } from "motion/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Search, Zap } from "lucide-react";

interface Server {
  id: string;
  flag: string;
  country: string;
  city: string;
  ping: number;
}

const servers: Server[] = [
  { id: "nl-ams", flag: "🇳🇱", country: "Netherlands", city: "Amsterdam", ping: 45 },
  { id: "de-fra", flag: "🇩🇪", country: "Germany", city: "Frankfurt", ping: 62 },
  { id: "us-ny", flag: "🇺🇸", country: "United States", city: "New York", ping: 128 },
  { id: "jp-tok", flag: "🇯🇵", country: "Japan", city: "Tokyo", ping: 210 },
  { id: "gb-lon", flag: "🇬🇧", country: "United Kingdom", city: "London", ping: 58 },
  { id: "fr-par", flag: "🇫🇷", country: "France", city: "Paris", ping: 52 },
  { id: "sg-sin", flag: "🇸🇬", country: "Singapore", city: "Singapore", ping: 185 },
  { id: "ca-tor", flag: "🇨🇦", country: "Canada", city: "Toronto", ping: 115 },
];

export function ServerListScreen() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedServer, setSelectedServer] = useState("nl-ams");

  const filteredServers = servers.filter((server) =>
    server.country.toLowerCase().includes(searchQuery.toLowerCase()) ||
    server.city.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getPingColor = (ping: number) => {
    if (ping < 80) return "#00C853";
    if (ping < 150) return "#FFB300";
    return "#FF3D57";
  };

  const handleServerSelect = (serverId: string) => {
    setSelectedServer(serverId);
    setTimeout(() => {
      navigate("/home");
    }, 300);
  };

  return (
    <div className="min-h-screen w-full bg-[#0D0F14] flex flex-col">
      {/* Header */}
      <div className="p-6 space-y-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/home")}
            className="p-2 hover:bg-[#1A1D26] rounded-lg transition-colors"
          >
            <ArrowLeft className="text-[#F0F2F5]" size={24} />
          </button>
          <h1 className="text-2xl font-semibold text-[#F0F2F5]">
            Выберите сервер
          </h1>
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
            placeholder="Поиск по стране..."
            className="w-full bg-[#252830] text-[#F0F2F5] pl-12 pr-4 py-3 rounded-xl border-2 border-transparent focus:border-[#00E5FF] focus:shadow-[0_0_20px_rgba(0,229,255,0.2)] transition-all outline-none"
          />
        </div>
      </div>

      {/* Server list */}
      <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-3">
        {/* Quick connect */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => handleServerSelect(servers[0].id)}
          className="w-full bg-gradient-to-r from-[#1A1D26] to-[#252830] hover:from-[#252830] hover:to-[#1A1D26] rounded-xl p-4 transition-all border border-[#00E5FF]/30"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#00E5FF] rounded-full flex items-center justify-center">
              <Zap size={20} className="text-[#0D0F14]" />
            </div>
            <div className="text-left flex-1">
              <p className="text-[#F0F2F5] font-semibold">
                Быстрое подключение
              </p>
              <p className="text-[#8B8F9A] text-sm">
                Автоматический выбор лучшего сервера
              </p>
            </div>
          </div>
        </motion.button>

        {/* Server list */}
        <div className="space-y-2">
          {filteredServers.map((server, index) => (
            <motion.button
              key={server.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => handleServerSelect(server.id)}
              className={`w-full rounded-xl p-4 transition-all flex items-center justify-between ${
                selectedServer === server.id
                  ? "bg-[#1A1D26] border-2 border-[#00E5FF]"
                  : "bg-[#1A1D26] hover:bg-[#252830] border-2 border-transparent"
              }`}
            >
              <div className="flex items-center gap-4">
                <span className="text-4xl">{server.flag}</span>
                <div className="text-left">
                  <p className="text-[#F0F2F5] font-semibold">
                    {server.country}
                  </p>
                  <p className="text-[#8B8F9A] text-sm">{server.city}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: getPingColor(server.ping) }}
                />
                <span
                  className="font-mono text-sm font-medium"
                  style={{ color: getPingColor(server.ping) }}
                >
                  {server.ping}ms
                </span>
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
}
