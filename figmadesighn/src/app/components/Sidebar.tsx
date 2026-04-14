import { NavLink } from "react-router";
import {
  Home,
  Users,
  Users2,
  FileText,
  Server,
  CreditCard,
  FileCheck,
  Shield,
  Activity,
  Settings
} from "lucide-react";

const sections = [
  {
    title: "ОБЗОР",
    items: [
      { icon: Home, label: "Главная", path: "/" },
    ],
  },
  {
    title: "УПРАВЛЕНИЕ",
    items: [
      { icon: Users, label: "Клиенты", path: "/users" },
      { icon: Users2, label: "Группы", path: "/groups" },
      { icon: FileText, label: "Шаблоны конфигов", path: "/config-profiles" },
      { icon: Server, label: "Серверы (Узлы)", path: "/nodes" },
    ],
  },
  {
    title: "ПОДПИСКИ",
    items: [
      { icon: CreditCard, label: "Тарифы", path: "/templates" },
      { icon: FileCheck, label: "Правила биллинга", path: "/response-rules" },
    ],
  },
  {
    title: "ИНСТРУМЕНТЫ",
    items: [
      { icon: Shield, label: "Контроль устройств", path: "/hwid-inspector" },
      { icon: Activity, label: "Логи подключений", path: "/connection-logs" },
    ],
  },
  {
    title: "СИСТЕМА",
    items: [
      { icon: Settings, label: "Настройки", path: "/settings" },
    ],
  },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col">
      <div className="p-6 border-b border-sidebar-border">
        <h1 className="text-xl font-bold text-primary">ShadeVPN</h1>
        <p className="text-xs text-muted-foreground mt-1">Админ Панель v2.0</p>
      </div>

      <nav className="flex-1 overflow-y-auto p-4 space-y-6">
        {sections.map((section) => (
          <div key={section.title}>
            <h2 className="text-xs font-semibold text-muted-foreground mb-2 px-3">
              {section.title}
            </h2>
            <div className="space-y-1">
              {section.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-sidebar-foreground hover:bg-sidebar-accent"
                    }`
                  }
                >
                  <item.icon className="w-4 h-4" />
                  <span className="text-sm">{item.label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>
    </aside>
  );
}
