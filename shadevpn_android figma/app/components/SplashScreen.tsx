import { motion } from "motion/react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export function SplashScreen() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      // Check if user has a key (for demo, we'll assume no key on first load)
      const hasKey = localStorage.getItem("shadeVPN_key");
      navigate(hasKey ? "/home" : "/onboarding", { replace: true });
    }, 2000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-[#0D0F14]">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col items-center"
      >
        {/* Logo - metallic S with cyan glow */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="relative mb-6"
        >
          <div className="text-8xl font-bold text-[#F0F2F5] relative">
            <span className="relative inline-block">
              S
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "100%" }}
                transition={{ delay: 0.5, duration: 0.8 }}
                className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[#00E5FF] to-transparent opacity-50 blur-xl"
                style={{ zIndex: -1 }}
              />
            </span>
          </div>
        </motion.div>

        {/* Logo text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="text-3xl font-semibold"
        >
          <span className="text-[#F0F2F5]">Shade</span>
          <span className="text-[#00E5FF]">VPN</span>
        </motion.div>
      </motion.div>

      {/* Bottom text */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.6 }}
        className="absolute bottom-8 text-[#8B8F9A] text-sm"
      >
        Powered by ShadeVPN
      </motion.div>
    </div>
  );
}
