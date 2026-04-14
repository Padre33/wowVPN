import { useState, useEffect, useRef } from "react";
import { Plus, Users as UsersIcon, Trash2, Edit, UserPlus, ChevronDown } from "lucide-react";
import { useNavigate } from "react-router";
import { API } from "../config";

export function Groups() {
  const [groups, setGroups] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [assignGroupId, setAssignGroupId] = useState<string | null>(null);
  const navigate = useNavigate();
  const [selectedClients, setSelectedClients] = useState<string[]>([]);
  const nameRef = useRef<HTMLInputElement>(null);
  const descRef = useRef<HTMLInputElement>(null);
  const limitRef = useRef<HTMLInputElement>(null);

  const loadGroups = () => fetch(`${API}/groups`).then(r => r.json()).then(setGroups).catch(() => {});
  const loadClients = () => fetch(`${API}/clients`).then(r => r.json()).then(setClients).catch(() => {});
  useEffect(() => { loadGroups(); loadClients(); }, []);

  const handleCreate = async () => {
    const name = nameRef.current?.value?.trim();
    if (!name) { alert("Введите название группы"); return; }
    if (editId) {
      await fetch(`${API}/groups/${editId}`, {
        method: "PATCH", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ name, description: descRef.current?.value || "", data_limit: limitRef.current?.value || "100 ГБ/юзер" }),
      });
    } else {
      await fetch(`${API}/groups`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ name, description: descRef.current?.value || "", data_limit: limitRef.current?.value || "100 ГБ/юзер" }),
      });
    }
    setShowForm(false); setEditId(null); loadGroups();
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Удалить группу? Клиенты будут отвязаны от неё.")) return;
    await fetch(`${API}/groups/${id}`, { method: "DELETE" });
    loadGroups(); loadClients();
  };

  const startEdit = (g: any) => {
    setEditId(g.id); setShowForm(true);
    setTimeout(() => {
      if (nameRef.current) nameRef.current.value = g.name;
      if (descRef.current) descRef.current.value = g.description;
      if (limitRef.current) limitRef.current.value = g.dataLimit;
    }, 50);
  };

  const openAssignPanel = (groupId: string) => {
    setAssignGroupId(groupId);
    setSelectedClients([]);
  };

  const toggleClientSelection = (clientId: string) => {
    setSelectedClients(prev =>
      prev.includes(clientId) ? prev.filter(id => id !== clientId) : [...prev, clientId]
    );
  };

  const handleAssign = async () => {
    if (!assignGroupId || selectedClients.length === 0) return;
    await fetch(`${API}/groups/${assignGroupId}/assign`, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ client_ids: selectedClients, group_id: assignGroupId }),
    });
    setAssignGroupId(null); setSelectedClients([]);
    loadGroups(); loadClients();
  };

  const groupMembers = (groupId: string) => clients.filter(c => c.groupId === groupId);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Группы</h1>
          <p className="text-muted-foreground mt-1">Организация клиентов по категориям</p>
        </div>
        <button onClick={() => { setEditId(null); setShowForm(true); }} className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
          <Plus className="w-4 h-4" /> Создать группу
        </button>
      </div>

      {/* ═══ Форма создания / редактирования ═══ */}
      {showForm && (
        <div className="p-6 rounded-lg border border-primary/30 bg-card space-y-4">
          <h3 className="font-bold text-lg">{editId ? "Редактировать группу" : "Новая группа"}</h3>
          <input ref={nameRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none" placeholder="Название группы (напр. VIP)" />
          <input ref={descRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none" placeholder="Описание (напр. Премиум безлимитный доступ)" />
          <input ref={limitRef} className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none" placeholder="Лимит трафика (напр. Безлимит)" defaultValue="100 ГБ/юзер" />
          <div className="flex gap-3">
            <button onClick={handleCreate} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">{editId ? "Сохранить" : "Создать"}</button>
            <button onClick={() => { setShowForm(false); setEditId(null); }} className="px-4 py-2 bg-muted rounded-lg">Отмена</button>
          </div>
        </div>
      )}

      {/* ═══ Панель назначения клиентов в группу ═══ */}
      {assignGroupId && (
        <div className="p-6 rounded-lg border-2 border-primary bg-card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-lg">
              Добавить клиентов в группу «{groups.find(g => g.id === assignGroupId)?.name}»
            </h3>
            <button onClick={() => setAssignGroupId(null)} className="text-muted-foreground hover:text-foreground">✕</button>
          </div>

          {clients.length === 0 ? (
            <p className="text-muted-foreground text-sm">Нет клиентов. Сначала создайте клиента на вкладке «Клиенты».</p>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">Выберите клиентов для добавления в группу:</p>
              <div className="max-h-60 overflow-y-auto space-y-1 border border-border rounded-lg p-2">
                {clients.map(c => (
                  <label key={c.id} className={`flex items-center gap-3 p-2 rounded hover:bg-muted/50 cursor-pointer transition-colors ${selectedClients.includes(c.id) ? 'bg-primary/10' : ''}`}>
                    <input
                      type="checkbox"
                      checked={selectedClients.includes(c.id)}
                      onChange={() => toggleClientSelection(c.id)}
                      className="w-4 h-4 rounded"
                    />
                    <span className="font-medium">{c.username}</span>
                    <span className="text-xs text-muted-foreground ml-auto">
                      {c.groupName !== "—" ? `Группа: ${c.groupName}` : "Без группы"}
                    </span>
                  </label>
                ))}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleAssign}
                  disabled={selectedClients.length === 0}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
                >
                  Добавить {selectedClients.length > 0 ? `(${selectedClients.length})` : ""} в группу
                </button>
                <button onClick={() => setAssignGroupId(null)} className="px-4 py-2 bg-muted rounded-lg">Отмена</button>
              </div>
            </>
          )}
        </div>
      )}

      {groups.length === 0 && !showForm && (
        <div className="p-8 text-center text-muted-foreground rounded-lg border border-dashed border-border">
          Нет групп. Нажмите «Создать группу» чтобы начать.
        </div>
      )}

      {/* ═══ Карточки групп ═══ */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
        {groups.map((group) => (
          <div 
            key={group.id} 
            onClick={() => navigate(`/users?group=${group.id}`)}
            className="p-5 rounded-lg border border-primary/30 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm hover:border-primary cursor-pointer transition-all shadow-sm hover:shadow-md"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="p-2.5 rounded-lg bg-primary/10"><UsersIcon className="w-5 h-5 text-primary" /></div>
              <div className="flex gap-1" onClick={e => e.stopPropagation()}>
                <button onClick={() => openAssignPanel(group.id)} className="p-1.5 hover:bg-primary/20 rounded transition-colors" title="Добавить клиентов"><UserPlus className="w-4 h-4" /></button>
                <button onClick={() => startEdit(group)} className="p-1.5 hover:bg-primary/20 rounded transition-colors" title="Редактировать"><Edit className="w-4 h-4" /></button>
                <button onClick={() => handleDelete(group.id)} className="p-1.5 hover:bg-destructive/20 text-destructive rounded transition-colors" title="Удалить"><Trash2 className="w-4 h-4" /></button>
              </div>
            </div>
            <h3 className="text-lg font-bold mb-1 truncate">{group.name}</h3>
            <p className="text-sm text-muted-foreground mb-4">{group.description || "Без описания"}</p>

            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between"><span className="text-muted-foreground">Участников</span><span className="font-semibold">{group.members}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Лимит</span><span className="font-semibold">{group.dataLimit}</span></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
