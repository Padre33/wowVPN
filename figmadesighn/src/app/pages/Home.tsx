import { useState, useEffect } from "react";
import { Cpu, HardDrive, MemoryStick, Clock, Calendar, CalendarDays, CalendarCheck, CalendarRange, Timer } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { API } from "../config";

function formatBytes(gb: number): string {
  if (gb >= 1024) return `${(gb / 1024).toFixed(1)} TB`;
  if (gb >= 1) return `${gb.toFixed(2)} GB`;
  if (gb > 0) return `${(gb * 1024).toFixed(1)} MB`;
  return "0";
}

export function Home() {
  const [dash, setDash] = useState<any>(null);
  const [sys, setSys] = useState<any>(null);
  const [clients, setClients] = useState<any[]>([]);
  const [trafficSummary, setTrafficSummary] = useState<any>(null);
  const [chartData, setChartData] = useState<any[]>([]);

  useEffect(() => {
    fetch(`${API}/dashboard`).then(r => r.json()).then(setDash).catch(() => {});
    fetch(`${API}/system`).then(r => r.json()).then(setSys).catch(() => {});
    fetch(`${API}/clients`).then(r => r.json()).then(setClients).catch(() => {});
    fetch(`${API}/traffic/summary`).then(r => r.json()).then(setTrafficSummary).catch(() => {});
    fetch(`${API}/traffic/chart24h`).then(r => r.json()).then(setChartData).catch(() => {});
  }, []);

  const activeCount = dash?.activeClients || 0;
  const disabledCount = dash?.disabledClients || 0;
  const totalCount = dash?.totalClients || 0;
  const downloadGB = dash?.downloadGB || 0;
  const uploadGB = dash?.uploadGB || 0;

  // Системные метрики — РЕАЛЬНЫЕ
  const systemCards = [
    {
      icon: MemoryStick, label: "Оперативная память",
      value: sys ? `${sys.memory_used_gb} / ${sys.memory_total_gb} GB` : "—",
      sub: sys ? `${sys.memory_percent}%` : "",
      color: "#06B6D4",
    },
    {
      icon: Cpu, label: "Загрузка ЦП",
      value: sys ? `${sys.cpu_percent}%` : "—",
      sub: "",
      color: "#8B5CF6",
    },
    {
      icon: HardDrive, label: "Свободно на диске",
      value: sys ? `${sys.disk_free_gb} GB` : "—",
      sub: sys ? `из ${sys.disk_total_gb} GB (${sys.disk_percent}%)` : "",
      color: "#10B981",
    },
    {
      icon: Clock, label: "Аптайм сервера",
      value: sys?.uptime_human || "—",
      sub: "",
      color: "#F59E0B",
    },
  ];

  // Bandwidth карточки — РЕАЛЬНЫЕ из снапшотов
  const ts = trafficSummary;
  const bandwidthCards = [
    { period: "За сегодня", value: formatBytes(ts?.todayGB || 0), icon: Timer, color: "#06B6D4" },
    { period: "За 7 дней", value: formatBytes(ts?.last7daysGB || 0), icon: CalendarDays, color: "#10B981" },
    { period: "За 30 дней", value: formatBytes(ts?.last30daysGB || 0), icon: CalendarRange, color: "#8B5CF6" },
    { period: "Текущий месяц", value: formatBytes(ts?.currentMonthGB || 0), icon: Calendar, color: "#F59E0B" },
    { period: "Текущий год", value: formatBytes(ts?.currentYearGB || 0), icon: CalendarCheck, color: "#10B981" },
  ];

  // Круговые диаграммы
  const pieCharts = [
    { title: "Клиенты", data: [
      { name: "Активные", value: activeCount, color: "#10B981" },
      { name: "Заблокированные", value: disabledCount, color: "#334155" },
    ]},
    { title: "За сегодня", data: [
      { name: "Заходили сегодня", value: activeCount, color: "#06B6D4" },
      { name: "Не заходили", value: Math.max(disabledCount, 0), color: "#334155" },
    ]},
    { title: "На этой неделе", data: [
      { name: "Заходили на неделе", value: totalCount, color: "#8B5CF6" },
      { name: "Никогда не заходили", value: 0, color: "#F43F5E" },
    ]},
  ];

  const sortedClients = [...clients].sort((a, b) => b.dataUsage - a.dataUsage);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary">Командный центр</h1>
        <p className="text-muted-foreground mt-1">
          Мониторинг инфраструктуры ShadeVPN в реальном времени
        </p>
        {dash && (
          <div className="mt-3 flex gap-3 text-sm flex-wrap">
            <span className="px-3 py-1 rounded-full bg-primary/20 text-primary font-medium">👥 Клиентов: {totalCount}</span>
            <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 font-medium">✅ Активных: {activeCount}</span>
            <span className="px-3 py-1 rounded-full bg-muted text-muted-foreground font-medium">⬇ {formatBytes(downloadGB)}</span>
            <span className="px-3 py-1 rounded-full bg-muted text-muted-foreground font-medium">⬆ {formatBytes(uploadGB)}</span>
          </div>
        )}
      </div>

      {/* ═══ Системные метрики — РЕАЛЬНЫЕ ═══ */}
      <section>
        <h2 className="text-sm font-semibold text-muted-foreground mb-4">НАГРУЗКА НА СИСТЕМУ</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {systemCards.map((card, i) => (
            <div key={i} className="p-5 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
              <div className="flex items-start justify-between mb-3">
                <p className="text-xs text-muted-foreground">{card.label}</p>
                <div className="p-2 rounded-lg" style={{ backgroundColor: `${card.color}20` }}>
                  <card.icon className="w-4 h-4" style={{ color: card.color }} />
                </div>
              </div>
              <p className="text-2xl font-bold">{card.value}</p>
              {card.sub && <p className="text-xs text-muted-foreground mt-1">{card.sub}</p>}
            </div>
          ))}
        </div>
      </section>

      {/* ═══ Потребление трафика — РЕАЛЬНЫЕ ═══ */}
      <section>
        <h2 className="text-sm font-semibold text-muted-foreground mb-4">ПОТРЕБЛЕНИЕ ТРАФИКА</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {bandwidthCards.map((card, i) => (
            <div key={i} className="p-5 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
              <div className="flex items-start justify-between mb-3">
                <p className="text-sm text-muted-foreground">{card.period}</p>
                <div className="p-2 rounded-full" style={{ backgroundColor: `${card.color}20` }}>
                  <card.icon className="w-4 h-4" style={{ color: card.color }} />
                </div>
              </div>
              <p className="text-3xl font-bold">{card.value}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ График 24 часа — РЕАЛЬНЫЙ ═══ */}
      <section>
        <h2 className="text-sm font-semibold text-muted-foreground mb-4">ТРАФИК (ЗА 24 ЧАСА)</h2>
        <div className="p-6 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData.length > 0 ? chartData : [{ time: "—", traffic: 0 }]}>
              <defs>
                <linearGradient id="trafficGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#94A3B8" fontSize={12} />
              <YAxis stroke="#94A3B8" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: "#1E293B", border: "1px solid #06B6D4", borderRadius: "8px" }}
                formatter={(value: number) => [`${value} GB`, "Трафик"]}
              />
              <Area type="monotone" dataKey="traffic" stroke="#06B6D4" strokeWidth={2} fill="url(#trafficGrad)" dot={{ fill: "#06B6D4", r: 3 }} />
            </AreaChart>
          </ResponsiveContainer>
          {chartData.length === 0 && (
            <p className="text-center text-muted-foreground text-sm mt-2">
              Нет данных — график заполнится после подключения к VPS
            </p>
          )}
        </div>
      </section>

      {/* ═══ Статистика онлайна ═══ */}
      <section>
        <h2 className="text-sm font-semibold text-muted-foreground mb-4">СТАТИСТИКА ОНЛАЙНА</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {pieCharts.map(({ title, data }) => (
            <div key={title} className="p-6 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
              <h3 className="text-sm text-muted-foreground mb-4">{title}</h3>
              <div className="flex items-center gap-6">
                <ResponsiveContainer width={120} height={120}>
                  <PieChart>
                    <Pie data={data} cx="50%" cy="50%" innerRadius={35} outerRadius={60} paddingAngle={5} dataKey="value">
                      {data.map((entry, idx) => <Cell key={idx} fill={entry.color} />)}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-2">
                  {data.map((item) => (
                    <div key={item.name} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded" style={{ backgroundColor: item.color }}></div>
                      <span className="text-sm">{item.name}</span>
                      <span className="text-sm font-bold ml-auto">{item.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ Трафик по клиентам ═══ */}
      {clients.length > 0 && (
        <section>
          <h2 className="text-sm font-semibold text-muted-foreground mb-4">ТРАФИК ПО КЛИЕНТАМ</h2>
          <div className="rounded-lg border border-primary/30 bg-card overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50 border-b border-border">
                <tr>
                  <th className="p-4 text-left text-xs font-semibold text-muted-foreground">КЛИЕНТ</th>
                  <th className="p-4 text-left text-xs font-semibold text-muted-foreground">СТАТУС</th>
                  <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ГРУППА</th>
                  <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ИСПОЛЬЗОВАНО</th>
                  <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ЛИМИТ</th>
                  <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ПРОГРЕСС</th>
                </tr>
              </thead>
              <tbody>
                {sortedClients.map((c) => {
                  const pct = c.dataLimit > 0 ? Math.min((c.dataUsage / c.dataLimit) * 100, 100) : 0;
                  const barColor = pct > 90 ? "#F43F5E" : pct > 70 ? "#F59E0B" : "#10B981";
                  return (
                    <tr key={c.id} className="border-b border-border hover:bg-muted/30 transition-colors">
                      <td className="p-4 font-medium">{c.username}</td>
                      <td className="p-4">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${c.status === "online" ? "bg-[#10B981]/20 text-[#10B981]" : "bg-muted text-muted-foreground"}`}>
                          {c.status === "online" ? "АКТИВЕН" : "ЗАБЛОКИРОВАН"}
                        </span>
                      </td>
                      <td className="p-4 text-sm text-muted-foreground">{c.groupName || "—"}</td>
                      <td className="p-4 text-sm font-mono">{formatBytes(c.dataUsage)}</td>
                      <td className="p-4 text-sm font-mono">{c.dataLimit >= 999 ? "Безлимит" : `${c.dataLimit} GB`}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                            <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: barColor }}></div>
                          </div>
                          <span className="text-xs text-muted-foreground w-8">{pct.toFixed(0)}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
