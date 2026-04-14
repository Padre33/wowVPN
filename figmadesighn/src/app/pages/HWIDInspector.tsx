import { useState, useEffect } from "react";
import { Shield, AlertTriangle, RefreshCw } from "lucide-react";
import { API } from "../config";

export function HWIDInspector() {
  const [clients, setClients] = useState<any[]>([]);

  const load = () => fetch(`${API}/clients`).then(r => r.json()).then(setClients).catch(() => {});
  useEffect(() => { load(); }, []);

  const total = clients.length;
  const safe = clients.filter(c => c.status === "online").length;
  const suspicious = total - safe;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Контроль Устройств</h1>
          <p className="text-muted-foreground mt-1">Отслеживание устройств и анти-шаринг</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 px-4 py-2 bg-muted text-foreground rounded-lg hover:bg-muted/80 transition-colors">
          <RefreshCw className="w-4 h-4" /> Обновить
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
          <p className="text-xs text-muted-foreground mb-2">Всего отслеживается</p>
          <p className="text-3xl font-bold">{total}</p>
        </div>
        <div className="p-5 rounded-lg border border-[#10B981]/30 bg-gradient-to-br from-card to-[#10B981]/5">
          <p className="text-xs text-muted-foreground mb-2">Активные аккаунты</p>
          <p className="text-3xl font-bold text-[#10B981]">{safe}</p>
        </div>
        <div className="p-5 rounded-lg border border-[#F43F5E]/30 bg-gradient-to-br from-card to-[#F43F5E]/5">
          <p className="text-xs text-muted-foreground mb-2">Заблокированные</p>
          <p className="text-3xl font-bold text-[#F43F5E]">{suspicious}</p>
        </div>
      </div>

      <div className="rounded-lg border border-primary/30 bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">СТАТУС</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ИМЯ КЛИЕНТА</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">TELEGRAM</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">VPN IP</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ГРУППА</th>
              </tr>
            </thead>
            <tbody>
              {clients.length === 0 && (
                <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Нет клиентов для отслеживания</td></tr>
              )}
              {clients.map((c) => (
                <tr key={c.id} className={`border-b border-border hover:bg-muted/30 transition-colors ${c.status === "offline" ? "bg-[#F43F5E]/5" : ""}`}>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      {c.status === "online" ? <Shield className="w-4 h-4 text-[#10B981]" /> : <AlertTriangle className="w-4 h-4 text-[#F43F5E]" />}
                      <span className={`text-xs font-semibold ${c.status === "online" ? "text-[#10B981]" : "text-[#F43F5E]"}`}>
                        {c.status === "online" ? "АКТИВЕН" : "ЗАБЛОКИРОВАН"}
                      </span>
                    </div>
                  </td>
                  <td className="p-4 font-medium">{c.username}</td>
                  <td className="p-4 text-muted-foreground">{c.telegramId}</td>
                  <td className="p-4 font-mono text-sm">{c.vpnIp}</td>
                  <td className="p-4"><span className="px-2 py-0.5 rounded bg-muted text-xs">{c.groupName || "—"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
