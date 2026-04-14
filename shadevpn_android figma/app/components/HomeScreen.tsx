import { motion } from "motion/react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Power, Settings, ChevronRight } from "lucide-react";

type ConnectionStatus = "disconnected" | "connecting" | "connected";

interface SessionStats {
  duration: string;
  download: string;
  upload: string;
}

export function HomeScreen() {
  const navigate = useNavigate();
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [stats, setStats] = useState<SessionStats>({
    duration: "00:00:00",
    download: "0.0 MB",
    upload: "0.0 MB",
  });
  const [currentServer] = useState({
    flag: "🇳🇱",
    country: "Netherlands",
    city: "Amsterdam",
    ping: 45,
  });

  // Simulate connection timer
  useEffect(() => {
    if (status === "connected") {
      let seconds = 0;
      const interval = setInterval(() => {
        seconds++;
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        setStats((prev) => ({
          ...prev,
          duration: `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`,
          download: `${(Math.random() * 200 + 100).toFixed(1)} MB`,
          upload: `${(Math.random() * 50 + 10).toFixed(1)} MB`,
        }));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [status]);

  const handleConnect = () => {
    if (status === "disconnected") {
      setStatus("connecting");
      setTimeout(() => {
        setStatus("connected");
      }, 2000);
    } else if (status === "connected") {
      setStatus("disconnected");
      setStats({
        duration: "00:00:00",
        download: "0.0 MB",
        upload: "0.0 MB",
      });
    }
  };

  const getPingColor = (ping: number) => {
    if (ping < 80) return "#00C853";
    if (ping < 150) return "#FFB300";
    return "#FF3D57";
  };

  return (
    <div className="min-h-screen w-full bg-[#0D0F14] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6">
        <div className="text-2xl font-bold">
          <span className="text-[#F0F2F5]">S</span>
        </div>
        <button
          onClick={() => navigate("/settings")}
          className="p-2 hover:bg-[#1A1D26] rounded-lg transition-colors"
        >
          <Settings className="text-[#8B8F9A]" size={24} />
        </button>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 pb-32">
        {/* Connection button */}
        <motion.div
          className="relative mb-8"
          whileTap={{ scale: 0.95 }}
        >
          {/* Glow ring for connected state */}
          {status === "connected" && (
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: "radial-gradient(circle, rgba(0,229,255,0.3) 0%, transparent 70%)",
                filter: "blur(20px)",
              }}
              animate={{
                scale: [1, 1.1, 1],
                opacity: [0.5, 0.8, 0.5],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          )}

          {/* Loading ring for connecting state */}
          {status === "connecting" && (
            <motion.div
              className="absolute inset-0 rounded-full border-4 border-transparent border-t-[#00E5FF]"
              animate={{ rotate: 360 }}
              transition={{
                duration: 1,
                repeat: Infinity,
                ease: "linear",
              }}
              style={{ width: "140px", height: "140px", margin: "-10px" }}
            />
          )}

          <button
            onClick={handleConnect}
            disabled={status === "connecting"}
            className={`relative w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${
              status === "disconnected"
                ? "bg-[#252830]"
                : status === "connecting"
                ? "bg-[#1A1D26]"
                : "bg-[#00E5FF] shadow-[0_0_40px_rgba(0,229,255,0.5)]"
            }`}
          >
            <Power
              size={48}
              className={`${
                status === "connected" ? "text-[#0D0F14]" : "text-[#00E5FF]"
              } transition-colors`}
            />
          </button>
        </motion.div>

        {/* Status text */}
        <motion.div
          key={status}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <p className="text-[#F0F2F5] text-lg font-medium">
            {status === "disconnected" && "Нажмите для подключения"}
            {status === "connecting" && "Подключение..."}
            {status === "connected" && "Защищено ✓"}
          </p>
        </motion.div>

        {/* Stats (only when connected) */}
        {status === "connected" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-xs space-y-3"
          >
            <div className="text-center">
              <p className="text-[#8B8F9A] text-sm mb-1">Время сессии</p>
              <p className="text-[#F0F2F5] text-2xl font-mono font-semibold">
                {stats.duration}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-[#8B8F9A] text-xs mb-1">⬇ Загрузка</p>
                <p className="text-[#F0F2F5] font-mono">{stats.download}</p>
              </div>
              <div>
                <p className="text-[#8B8F9A] text-xs mb-1">⬆ Выгрузка</p>
                <p className="text-[#F0F2F5] font-mono">{stats.upload}</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Server card */}
      <div className="p-6">
        <button
          onClick={() => navigate("/servers")}
          className="w-full bg-[#1A1D26] hover:bg-[#252830] rounded-xl p-4 transition-all flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <span className="text-3xl">{currentServer.flag}</span>
            <div className="text-left">
              <p className="text-[#F0F2F5] font-semibold">
                {currentServer.country}, {currentServer.city}
              </p>
              <p
                className="text-sm font-mono"
                style={{ color: getPingColor(currentServer.ping) }}
              >
                {currentServer.ping}ms
              </p>
            </div>
          </div>
          <ChevronRight className="text-[#8B8F9A]" size={20} />
        </button>
      </div>
    </div>
  );
}
