import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SplashScreen } from "./components/SplashScreen";
import { OnboardingScreen } from "./components/OnboardingScreen";
import { HomeScreen } from "./components/HomeScreen";
import { ServerListScreen } from "./components/ServerListScreen";
import { SettingsScreen } from "./components/SettingsScreen";
import { SplitTunnelingScreen } from "./components/SplitTunnelingScreen";

export default function App() {
  return (
    <BrowserRouter>
      <div className="size-full flex items-center justify-center bg-[#0D0F14]">
        <div className="w-full max-w-md h-full relative overflow-hidden shadow-2xl">
          <Routes>
            <Route path="/" element={<SplashScreen />} />
            <Route path="/onboarding" element={<OnboardingScreen />} />
            <Route path="/home" element={<HomeScreen />} />
            <Route path="/servers" element={<ServerListScreen />} />
            <Route path="/settings" element={<SettingsScreen />} />
            <Route path="/split-tunneling" element={<SplitTunnelingScreen />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}