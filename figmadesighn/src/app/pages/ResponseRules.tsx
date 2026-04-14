import { useState, useEffect, useRef } from "react";
import { Plus, Zap, ToggleLeft, ToggleRight, Trash2 } from "lucide-react";
import { API } from "../config";

export function ResponseRules() {
  const [rules, setRules] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const nameRef = useRef<HTMLInputElement>(null);
  const triggerRef = useRef<HTMLInputElement>(null);
  const actionRef = useRef<HTMLInputElement>(null);

  const load = () => fetch(`${API}/rules`).then(r => r.json()).then(setRules).catch(() => {});
  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    const name = nameRef.current?.value?.trim();
    const trigger = triggerRef.current?.value?.trim();
    const action = actionRef.current?.value?.trim();
    if (!name || !trigger || !action) { alert("Заполните все поля"); return; }
    await fetch(`${API}/rules`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ name, trigger, action, enabled: true }),
    });
    setShowForm(false); load();
  };

  const toggleRule = async (id: string, current: boolean) => {
    await fetch(`${API}/rules/${id}/toggle`, {
      method: "PATCH", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ enabled: !current }),
    });
    load();
  };

  const deleteRule = async (id: string) => {
    if (!confirm("Удалить это правило?")) return;
    await fetch(`${API}/rules/${id}`, { method: "DELETE" });
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Правила Биллинга</h1>
          <p className="text-muted-foreground mt-1">Автоматические действия на основе триггеров</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
          <Plus className="w-4 h-4" /> Создать правило
        </button>
      </div>

      {showForm && (
        <div className="p-6 rounded-lg border border-primary/30 bg-card space-y-4">
          <h3 className="font-bold text-lg">Новое правило</h3>
          <input ref={nameRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" placeholder="Название правила" />
          <input ref={triggerRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" placeholder="Триггер (напр. Трафик достигает 90% лимита)" />
          <input ref={actionRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" placeholder="Действие (напр. Отправить уведомление в Telegram)" />
          <div className="flex gap-3">
            <button onClick={handleCreate} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">Создать</button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 bg-muted rounded-lg">Отмена</button>
          </div>
        </div>
      )}

      {rules.length === 0 && !showForm && (
        <div className="p-8 text-center text-muted-foreground rounded-lg border border-dashed border-border">
          Нет правил. Нажмите «Создать правило» для добавления автоматизации.
        </div>
      )}

      <div className="space-y-3">
        {rules.map((rule) => (
          <div key={rule.id} className="p-5 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4 flex-1">
                <div className={`p-3 rounded-lg ${rule.enabled ? 'bg-primary/10' : 'bg-muted'}`}>
                  <Zap className={`w-5 h-5 ${rule.enabled ? 'text-primary' : 'text-muted-foreground'}`} />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold mb-2">{rule.name}</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-start gap-2">
                      <span className="text-muted-foreground min-w-20">Событие:</span>
                      <span>{rule.trigger}</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-muted-foreground min-w-20">Действие:</span>
                      <span>{rule.action}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleRule(rule.id, rule.enabled)}
                  className={`p-2 rounded transition-colors ${rule.enabled ? 'text-primary hover:bg-primary/20' : 'text-muted-foreground hover:bg-muted'}`}
                >
                  {rule.enabled ? <ToggleRight className="w-6 h-6" /> : <ToggleLeft className="w-6 h-6" />}
                </button>
                <button onClick={() => deleteRule(rule.id)} className="p-2 hover:bg-destructive/20 text-destructive rounded transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
