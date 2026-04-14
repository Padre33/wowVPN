import { useState } from "react";
import { API } from "../config";

export function Login({ onLogin }: { onLogin: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
      });

      if (res.ok) {
        localStorage.setItem("adminToken", password);
        onLogin();
      } else {
        setError("Неверный пароль");
      }
    } catch {
      setError("Ошибка соединения с сервером");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-sm bg-[#1A1F2E] border border-border rounded-xl shadow-2xl p-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-blue-500 to-indigo-500"></div>
        <h2 className="text-2xl font-bold text-center text-white mb-6">ShadeVPN Admin</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-1">
              Пароль администратора
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Введите пароль..."
              autoFocus
            />
          </div>
          
          {error && <p className="text-red-500 text-sm text-center font-medium animate-pulse">{error}</p>}
          
          <button
            type="submit"
            disabled={loading || !password}
            className="w-full bg-primary hover:bg-primary/90 text-white rounded-md py-2 px-4 font-medium transition-colors disabled:opacity-50"
          >
            {loading ? "Проверка..." : "Войти"}
          </button>
        </form>
      </div>
      <p className="mt-8 text-sm text-muted-foreground/50">Copyright © 2026</p>
    </div>
  );
}
