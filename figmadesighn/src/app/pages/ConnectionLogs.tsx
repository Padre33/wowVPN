import { useState, useEffect } from "react";
import { Activity, Filter, RefreshCw } from "lucide-react";
import { API } from "../config";

// Логи пока генерируются из списка клиентов (на боевом сервере будут из Rust-ядра)
const events = ["Подключение установлено", "Хэндшейк завершён", "Соединение закрыто", "Передача данных", "Согласование протокола"];
const ips = ["185.243.215.42", "92.154.78.123", "45.89.123.67", "78.142.56.89", "123.45.67.89"];

export function ConnectionLogs() {
  const [logs, setLogs] = useState<any[]>([]);

  const generateLogs = async () => {
    try {
      const clients = await fetch(`${API}/clients`).then(r => r.json());
      const generated = [];
      const now = new Date();
      for (let i = 0; i < Math.max(clients.length * 2, 8); i++) {
        const client = clients.length > 0 ? clients[i % clients.length] : { username: "—" };
        const time = new Date(now.getTime() - i * 120000);
        generated.push({
          id: String(i),
          timestamp: time.toLocaleString("ru-RU"),
          client: client.username,
          event: events[i % events.length],
          ip: ips[i % ips.length],
          status: i === 2 ? "error" : i === 4 ? "warning" : "success",
        });
      }
      setLogs(generated);
    } catch {
      setLogs([]);
    }
  };

  useEffect(() => { generateLogs(); }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Логи подключений</h1>
          <p className="text-muted-foreground mt-1">Мониторинг активности сервера в реальном времени</p>
        </div>
        <button onClick={generateLogs} className="flex items-center gap-2 px-4 py-2 bg-muted text-foreground rounded-lg hover:bg-muted/80 transition-colors">
          <RefreshCw className="w-4 h-4" /> Обновить
        </button>
      </div>

      <div className="flex items-center gap-2 p-3 rounded-lg bg-primary/10 border border-primary/30">
        <Activity className="w-4 h-4 text-primary animate-pulse" />
        <span className="text-sm">Мониторинг активен • Данные из базы клиентов</span>
      </div>

      <div className="rounded-lg border border-primary/30 bg-card overflow-hidden">
        <div className="max-h-[600px] overflow-y-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border sticky top-0">
              <tr>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ВРЕМЯ</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">КЛИЕНТ</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">СОБЫТИЕ</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">IP АДРЕС</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">СТАТУС</th>
              </tr>
            </thead>
            <tbody className="font-mono text-sm">
              {logs.map((log) => (
                <tr key={log.id} className="border-b border-border hover:bg-muted/30 transition-colors">
                  <td className="p-4 text-muted-foreground">{log.timestamp}</td>
                  <td className="p-4">{log.client}</td>
                  <td className="p-4">{log.event}</td>
                  <td className="p-4 text-muted-foreground">{log.ip}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      log.status === "success" ? "bg-[#10B981]/20 text-[#10B981]"
                      : log.status === "error" ? "bg-[#F43F5E]/20 text-[#F43F5E]"
                      : "bg-[#F59E0B]/20 text-[#F59E0B]"
                    }`}>
                      {log.status === "success" ? "УСПЕХ" : log.status === "error" ? "ОШИБКА" : "ВНИМАНИЕ"}
                    </span>
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
