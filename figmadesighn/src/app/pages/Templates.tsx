import { useState, useEffect, useRef } from "react";
import { Plus, CreditCard, Trash2 } from "lucide-react";
import { API } from "../config";

export function Templates() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const nameRef = useRef<HTMLInputElement>(null);
  const daysRef = useRef<HTMLInputElement>(null);
  const limitRef = useRef<HTMLInputElement>(null);
  const priceRef = useRef<HTMLInputElement>(null);

  const load = () => fetch(`${API}/templates`).then(r => r.json()).then(setTemplates).catch(() => {});
  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    const name = nameRef.current?.value?.trim();
    if (!name) { alert("Введите название тарифа"); return; }
    await fetch(`${API}/templates`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        name,
        duration_days: parseInt(daysRef.current?.value || "30"),
        data_limit_gb: parseFloat(limitRef.current?.value || "50"),
        price: priceRef.current?.value || "0",
      }),
    });
    setShowForm(false); load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Удалить этот тариф?")) return;
    await fetch(`${API}/templates/${id}`, { method: "DELETE" });
    load();
  };

  const durationLabel = (days: number) => {
    if (days >= 365) return `${Math.floor(days/365)} год`;
    if (days >= 30) return `${Math.floor(days/30)} мес.`;
    return `${days} дн.`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Шаблоны Тарифов</h1>
          <p className="text-muted-foreground mt-1">Предустановленные тарифные планы</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
          <Plus className="w-4 h-4" /> Новый тариф
        </button>
      </div>

      {showForm && (
        <div className="p-6 rounded-lg border border-primary/30 bg-card space-y-4">
          <h3 className="font-bold text-lg">Создать тариф</h3>
          <input ref={nameRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none" placeholder="Название (напр. VIP Безлимит)" />
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-muted-foreground">Дней</label>
              <input ref={daysRef} type="number" defaultValue="30" className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Лимит (ГБ)</label>
              <input ref={limitRef} type="number" defaultValue="50" className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Цена</label>
              <input ref={priceRef} defaultValue="$9.99" className="w-full px-3 py-2 bg-input rounded-lg border border-border outline-none" />
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={handleCreate} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">Создать</button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 bg-muted rounded-lg">Отмена</button>
          </div>
        </div>
      )}

      {templates.length === 0 && !showForm && (
        <div className="p-8 text-center text-muted-foreground rounded-lg border border-dashed border-border">
          Нет тарифов. Нажмите «Новый тариф» чтобы создать.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {templates.map((t) => (
          <div key={t.id} className="p-6 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm hover:border-primary/50 transition-colors">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 rounded-lg bg-primary/10"><CreditCard className="w-6 h-6 text-primary" /></div>
              <button onClick={() => handleDelete(t.id)} className="p-1.5 hover:bg-destructive/20 text-destructive rounded transition-colors"><Trash2 className="w-3.5 h-3.5" /></button>
            </div>
            <h3 className="text-lg font-bold mb-1">{t.name}</h3>
            <p className="text-2xl font-bold text-primary mb-4">{t.price === "0" ? "Бесплатно" : t.price}</p>
            <div className="space-y-2 text-sm border-t border-border pt-4">
              <div className="flex justify-between"><span className="text-muted-foreground">Длительность</span><span className="font-semibold">{durationLabel(t.durationDays)}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Лимит трафика</span><span className="font-semibold">{t.dataLimitGb >= 999 ? "Безлимит" : `${t.dataLimitGb} ГБ`}</span></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
