import { motion } from "motion/react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Key, Copy, Camera, Image } from "lucide-react";

export function OnboardingScreen() {
  const navigate = useNavigate();
  const [keyInput, setKeyInput] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setKeyInput(text);
      setError("");
    } catch (err) {
      console.error("Failed to read clipboard");
    }
  };

  const handleActivate = () => {
    if (!keyInput.trim()) {
      setError("Введите ключ подключения");
      return;
    }

    if (!keyInput.startsWith("shade://")) {
      setError("Неверный формат ключа");
      return;
    }

    setSuccess(true);
    localStorage.setItem("shadeVPN_key", keyInput);
    setTimeout(() => {
      navigate("/home", { replace: true });
    }, 600);
  };

  const handleScanQR = () => {
    // Mock QR scan - in real app would open camera
    alert("В реальном приложении откроется камера для сканирования QR-кода");
  };

  const handleUploadQR = () => {
    // Mock QR upload - in real app would open gallery
    alert("В реальном приложении откроется галерея для выбора изображения с QR-кодом");
  };

  return (
    <div className="min-h-screen w-full bg-[#0D0F14] flex flex-col items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md space-y-8"
      >
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="text-4xl font-bold mb-2">
            <span className="text-[#F0F2F5]">Shade</span>
            <span className="text-[#00E5FF]">VPN</span>
          </div>
        </div>

        {/* Welcome text */}
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-semibold text-[#F0F2F5]">
            Добро пожаловать
          </h1>
          <p className="text-[#8B8F9A]">
            Введите ваш ключ подключения или отсканируйте QR-код
          </p>
        </div>

        {/* Key input */}
        <div className="space-y-4">
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8B8F9A]">
              <Key size={18} />
            </div>
            <input
              type="text"
              value={keyInput}
              onChange={(e) => {
                setKeyInput(e.target.value);
                setError("");
                setSuccess(false);
              }}
              placeholder="shade://eyJ..."
              className={`w-full bg-[#252830] text-[#F0F2F5] pl-12 pr-24 py-4 rounded-xl border-2 transition-all outline-none ${
                error
                  ? "border-[#FF3D57]"
                  : success
                  ? "border-[#00C853]"
                  : "border-transparent focus:border-[#00E5FF] focus:shadow-[0_0_20px_rgba(0,229,255,0.2)]"
              }`}
            />
            <button
              onClick={handlePaste}
              className="absolute right-3 top-1/2 -translate-y-1/2 px-4 py-2 bg-[#1A1D26] hover:bg-[#252830] text-[#00E5FF] rounded-lg transition-colors text-sm font-medium flex items-center gap-2"
            >
              <Copy size={14} />
              Вставить
            </button>
          </div>

          {error && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-[#FF3D57] text-sm"
            >
              {error}
            </motion.p>
          )}

          <button
            onClick={handleActivate}
            className="w-full bg-[#00E5FF] hover:bg-[#00D4EE] text-[#0D0F14] py-4 rounded-xl font-semibold transition-all shadow-[0_0_20px_rgba(0,229,255,0.3)] hover:shadow-[0_0_30px_rgba(0,229,255,0.5)]"
          >
            Активировать ключ
          </button>
        </div>

        {/* Divider */}
        <div className="flex items-center gap-4">
          <div className="flex-1 h-px bg-[#252830]" />
          <span className="text-[#8B8F9A] text-sm">или</span>
          <div className="flex-1 h-px bg-[#252830]" />
        </div>

        {/* QR options */}
        <div className="space-y-3">
          <button
            onClick={handleScanQR}
            className="w-full bg-[#00E5FF] hover:bg-[#00D4EE] text-[#0D0F14] py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 shadow-[0_0_20px_rgba(0,229,255,0.3)]"
          >
            <Camera size={20} />
            Сканировать QR камерой
          </button>

          <button
            onClick={handleUploadQR}
            className="w-full bg-transparent hover:bg-[#1A1D26] text-[#00E5FF] py-4 rounded-xl font-semibold transition-all border-2 border-[#00E5FF] flex items-center justify-center gap-3"
          >
            <Image size={20} />
            Загрузить QR из галереи
          </button>
        </div>

        {/* Get key link */}
        <div className="text-center">
          <a
            href="#"
            className="text-[#00E5FF] hover:text-[#00D4EE] text-sm transition-colors"
          >
            Нет ключа? <span className="underline">Получить ключ</span>
          </a>
        </div>
      </motion.div>
    </div>
  );
}
