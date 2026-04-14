import { useState, useEffect } from "react";
import { Shield, Copy, RefreshCw } from "lucide-react";
import { API } from "../config";

export function ConfigProfiles() {
  const [clients, setClients] = useState<any[]>([]);
  const [copied, setCopied] = useState("");

  const load = () => fetch(`${API}/clients`).then(r => r.json()).then(setClients).catch(() => {});
  useEffect(() => { load(); }, []);

  const copyKey = (link: string, name: string) => {
    navigator.clipboard.writeText(link);
    setCopied(name);
    setTimeout(() => setCopied(""), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Ключи подключений</h1>
          <p className="text-muted-foreground mt-1">Все сгенерированные shade:// ключи для быстрого копирования</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 px-4 py-2 bg-muted text-foreground rounded-lg hover:bg-muted/80 transition-colors">
          <RefreshCw className="w-4 h-4" /> Обновить
        </button>
      </div>

      {clients.length === 0 && (
        <div className="p-8 text-center text-muted-foreground rounded-lg border border-dashed border-border">
          Нет клиентов. Создайте клиента на вкладке «Клиенты».
        </div>
      )}

      <div className="rounded-lg border border-primary/30 bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">КЛИЕНТ</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ПРОТОКОЛ</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">VPN IP</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">СТАТУС</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ДЕЙСТВИЯ</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((c) => (
                <tr key={c.id} className="border-b border-border hover:bg-muted/30 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded bg-primary/10"><Shield className="w-4 h-4 text-primary" /></div>
                      <span className="font-medium">{c.username}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-1 rounded bg-primary/20 text-primary text-xs">{c.protocol}</span>
                  </td>
                  <td className="p-4 font-mono text-sm">{c.vpnIp}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${c.status === "online" ? "bg-[#10B981]/20 text-[#10B981]" : "bg-muted text-muted-foreground"}`}>
                      {c.status === "online" ? "Активен" : "Заблокирован"}
                    </span>
                  </td>
                  <td className="p-4">
                    <button
                      onClick={() => copyKey(c.shadeLink, c.username)}
                      className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 text-primary rounded hover:bg-primary/20 transition-colors text-sm"
                    >
                      <Copy className="w-3.5 h-3.5" />
                      {copied === c.username ? "✅ Скопировано!" : "Скопировать ключ"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
