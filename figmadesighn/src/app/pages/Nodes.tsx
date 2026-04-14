import { useState, useEffect, useRef } from "react";
import { Server, Plus, Trash2 } from "lucide-react";
import { API } from "../config";

export function Nodes() {
  const [nodes, setNodes] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const nameRef = useRef<HTMLInputElement>(null);
  const locRef = useRef<HTMLInputElement>(null);
  const ipRef = useRef<HTMLInputElement>(null);
  const portRef = useRef<HTMLInputElement>(null);

  const load = () => fetch(`${API}/nodes`).then(r => r.json()).then(setNodes).catch(() => {});
  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    const name = nameRef.current?.value?.trim();
    if (!name) { alert("Введите название сервера"); return; }
    await fetch(`${API}/nodes`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        name,
        location: locRef.current?.value || "",
        ip_address: ipRef.current?.value || "",
        port: parseInt(portRef.current?.value || "443"),
      }),
    });
    setShowForm(false); load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Удалить этот сервер?")) return;
    await fetch(`${API}/nodes/${id}`, { method: "DELETE" });
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Серверы</h1>
          <p className="text-muted-foreground mt-1">Управление VPN-серверами и их инфраструктурой</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
          <Plus className="w-4 h-4" /> Добавить сервер
        </button>
      </div>

      {showForm && (
        <div className="p-6 rounded-lg border border-primary/30 bg-card space-y-4">
          <h3 className="font-bold text-lg">Новый сервер</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-muted-foreground">Название</label>
              <input ref={nameRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" placeholder="node-de-01" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Локация</label>
              <input ref={locRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" placeholder="Frankfurt, DE" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">IP адрес</label>
              <input ref={ipRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" placeholder="185.204.52.135" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Порт</label>
              <input ref={portRef} type="number" defaultValue="443" className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" />
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={handleCreate} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">Добавить</button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 bg-muted rounded-lg">Отмена</button>
          </div>
        </div>
      )}

      {nodes.length === 0 && !showForm && (
        <div className="p-8 text-center text-muted-foreground rounded-lg border border-dashed border-border">
          Нет серверов. Нажмите «Добавить сервер» для регистрации нового узла.
        </div>
      )}

      <div className="space-y-4">
        {nodes.map((node) => (
          <div key={node.id} className="p-6 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-primary/10"><Server className="w-6 h-6 text-primary" /></div>
                <div>
                  <h3 className="text-xl font-bold">{node.name}</h3>
                  <p className="text-sm text-muted-foreground">{node.location || "Локация не указана"}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${node.isOnline ? "bg-[#10B981]" : "bg-red-500"}`}></div>
                  <span className={`text-sm ${node.isOnline ? "text-[#10B981]" : "text-red-500"}`}>{node.isOnline ? "В сети" : "Не в сети"}</span>
                </div>
                <button onClick={() => handleDelete(node.id)} className="p-2 hover:bg-destructive/20 text-destructive rounded transition-colors"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-xs text-muted-foreground mb-1">IP Адрес</p>
                <p className="text-lg font-bold font-mono">{node.ipAddress || "—"}</p>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-xs text-muted-foreground mb-1">Порт</p>
                <p className="text-lg font-bold">{node.port}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
