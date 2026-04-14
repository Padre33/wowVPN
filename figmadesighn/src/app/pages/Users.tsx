import { useState, useEffect, useRef } from "react";
import { Plus, Trash2, RefreshCw, Eye, Copy, QrCode, ToggleLeft, ToggleRight, X } from "lucide-react";
import { QRCodeSVG } from "qrcode.react";
import { API } from "../config";

function formatBytes(gb: number): string {
  if (gb >= 1024) return `${(gb / 1024).toFixed(1)} TB`;
  if (gb >= 1) return `${gb.toFixed(2)} GB`;
  if (gb > 0) return `${(gb * 1024).toFixed(1)} MB`;
  return "0 MB";
}

export function Users() {
  const [users, setUsers] = useState<any[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedGroupId, setSelectedGroupId] = useState("");

  const nameRef = useRef<HTMLInputElement>(null);
  const tgRef = useRef<HTMLInputElement>(null);
  const limitRef = useRef<HTMLInputElement>(null);
  const dateRef = useRef<HTMLInputElement>(null);

  const [qrModal, setQrModal] = useState<{isOpen: boolean, link: string, username: string} | null>(null);

  const fetchUsers = () => fetch(`${API}/clients`).then(r => r.json()).then(setUsers).catch(() => {});

  const fetchGroups = () => fetch(`${API}/groups`).then(r => r.json()).then(setGroups).catch(() => {});
  const fetchTemplates = () => fetch(`${API}/templates`).then(r => r.json()).then(setTemplates).catch(() => {});

  useEffect(() => { 
    const fetchData = () => { fetchUsers(); fetchGroups(); fetchTemplates(); };
    fetchData(); 
    const interval = setInterval(fetchData, 5000); 
    return () => clearInterval(interval); 
  }, []);

  const toggleUserSelection = (userId: string) => {
    setSelectedUsers((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    );
  };

  const toggleSelectAll = () => {
    if (selectedUsers.length === users.length) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(users.map((u) => u.id));
    }
  };

  const openUserDetails = (user: any) => {
    setSelectedUser(user);
    setSidebarOpen(true);
  };

  // ─── Создание клиента ───
  const handleToggle = async (clientId: string, currentStatus: string) => {
    const enabled = currentStatus !== "online";
    await fetch(`${API}/clients/${clientId}/toggle`, {
      method: "PATCH", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ enabled }),
    });
    fetchUsers();
  };

  const handleTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const t = templates.find(t => t.id === e.target.value);
    if (t && limitRef.current) {
      limitRef.current.value = String(t.dataLimitGb);
    }
  };

  const handleCreate = async () => {
    const username = nameRef.current?.value?.trim();
    if (!username) { alert("Введите имя клиента!"); return; }

    setLoading(true);
    try {
      const res = await fetch(`${API}/clients`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          telegram_id: tgRef.current?.value || null,
          data_limit: parseFloat(limitRef.current?.value || "100"),
          group_id: selectedGroupId || null,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        alert(`Ошибка: ${err.detail || "Не удалось создать клиента"}`);
        return;
      }
      fetchUsers();
      setSidebarOpen(false);
    } catch (e) {
      alert("Сервер API недоступен. Убедитесь, что бэкенд запущен.");
    } finally {
      setLoading(false);
    }
  };

  // ─── Удаление одного клиента ───
  const handleDelete = async (clientId: string) => {
    if (!confirm("Удалить этого клиента? Его VPN-ключ будет деактивирован.")) return;
    try {
      await fetch(`${API}/clients/${clientId}`, { method: "DELETE" });
      fetchUsers();
      setSelectedUsers(prev => prev.filter(id => id !== clientId));
    } catch (e) {
      alert("Ошибка удаления");
    }
  };

  // ─── Массовое удаление ───
  const handleBulkDelete = async () => {
    if (!confirm(`Удалить ${selectedUsers.length} клиент(ов)? Это необратимо.`)) return;
    for (const id of selectedUsers) {
      await fetch(`${API}/clients/${id}`, { method: "DELETE" }).catch(() => {});
    }
    setSelectedUsers([]);
    fetchUsers();
  };

  // ─── Копировать ключ ───
  const copyKey = (shadeLink: string) => {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(shadeLink);
      alert("✅ Ключ shade:// скопирован в буфер обмена!");
    } else {
      const textArea = document.createElement("textarea");
      textArea.value = shadeLink;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        alert("✅ Ключ shade:// скопирован в буфер обмена (fallback грязным хаком)!");
      } catch (err) {
        alert("Не удалось скопировать ключ. Пожалуйста, выделите его вручную.");
      }
      document.body.removeChild(textArea);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Клиенты</h1>
          <p className="text-muted-foreground mt-1">
            Управление клиентами VPN и их подписками
          </p>
        </div>
        <button
          onClick={() => {
            setSelectedUser(null);
            setSidebarOpen(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Добавить клиента
        </button>
      </div>

      {selectedUsers.length > 0 && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-primary/10 border border-primary/30">
          <p className="text-sm">
            <span className="font-bold">{selectedUsers.length}</span> клиент(ов) выбрано
          </p>
          <button
            onClick={handleBulkDelete}
            className="flex items-center gap-2 px-3 py-1.5 bg-destructive text-destructive-foreground rounded hover:bg-destructive/90 transition-colors text-sm"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Удалить
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors text-sm">
            <RefreshCw className="w-3.5 h-3.5" />
            Сбросить трафик
          </button>
        </div>
      )}

      <div className="rounded-lg border border-primary/30 bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="p-4 text-left">
                  <input
                    type="checkbox"
                    checked={selectedUsers.length === users.length && users.length > 0}
                    onChange={toggleSelectAll}
                    className="rounded border-border"
                  />
                </th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ПОДПИСКА</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">СЕТЬ</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ИМЯ КЛИЕНТА</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">TELEGRAM ID</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ПРОТОКОЛ</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ТРАФИК</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ГРУППА</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ОКОНЧАНИЕ ПОДПИСКИ</th>
                <th className="p-4 text-left text-xs font-semibold text-muted-foreground">ДЕЙСТВИЯ</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 && (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-muted-foreground">
                    Нет клиентов. Нажмите «Добавить клиента» для регистрации.
                  </td>
                </tr>
              )}
              {users.map((user) => (
                <tr
                  key={user.id}
                  className="border-b border-border hover:bg-muted/30 transition-colors"
                >
                  <td className="p-4">
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(user.id)}
                      onChange={() => toggleUserSelection(user.id)}
                      className="rounded border-border"
                    />
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                       <div className={`w-2 h-2 rounded-full ${user.status === "online" ? "bg-[#10B981]" : "bg-red-500"}`}></div>
                       <span className={`text-sm ${user.status === "online" ? "text-gray-300" : "text-red-400"}`}>
                         {user.status === "online" ? "Активна" : "Заблокирована"}
                       </span>
                    </div>
                  </td>
                  <td className="p-4">
                    {user.isOnline ? (
                      <span className="inline-flex items-center space-x-1 text-[#10B981] bg-[#10B981]/10 px-2 py-1 rounded-full text-xs font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse"></span>
                        <span>В сети</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 text-gray-500 bg-gray-800/50 px-2 py-1 rounded-full text-xs font-medium border border-gray-700/50">
                        <span className="w-1.5 h-1.5 rounded-full bg-gray-500"></span>
                        <span>Офлайн</span>
                      </span>
                    )}
                  </td>
                  <td className="p-4 font-medium">{user.username}</td>
                  <td className="p-4 text-muted-foreground">{user.telegramId}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 rounded bg-primary/20 text-primary text-xs">
                      {user.protocol}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm">
                        <span>
                          {formatBytes(user.dataUsage)} / {user.dataLimit >= 999 ? "Безлимит" : `${user.dataLimit} GB`}
                        </span>
                      </div>
                      <div className="w-32 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full"
                          style={{
                            width: `${Math.min((user.dataUsage / user.dataLimit) * 100, 100)}%`,
                          }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-0.5 rounded bg-muted text-xs">{user.groupName || "—"}</span>
                  </td>
                  <td className="p-4 text-sm">{user.subscriptionEnd}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => openUserDetails(user)}
                        className="p-1.5 hover:bg-primary/20 rounded transition-colors"
                        title="Подробнее"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setQrModal({ isOpen: true, link: user.shadeLink, username: user.username })}
                        className="p-1.5 hover:bg-primary/20 rounded transition-colors"
                        title="Показать QR-код"
                      >
                        <QrCode className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => copyKey(user.shadeLink)}
                        className="p-1.5 hover:bg-primary/20 rounded transition-colors"
                        title="Скопировать ключ"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleToggle(user.id, user.status)}
                        className={`p-1.5 rounded transition-colors ${user.status === "online" ? "text-primary hover:bg-primary/20" : "text-muted-foreground hover:bg-muted"}`}
                        title={user.status === "online" ? "Заблокировать" : "Разблокировать"}
                      >
                        {user.status === "online" ? <ToggleRight className="w-5 h-5" /> : <ToggleLeft className="w-5 h-5" />}
                      </button>
                      <button
                        onClick={() => handleDelete(user.id)}
                        className="p-1.5 hover:bg-destructive/20 text-destructive rounded transition-colors"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sidebar */}
      {sidebarOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/50 z-40"
            onClick={() => setSidebarOpen(false)}
          ></div>
          <div className="fixed right-0 top-0 bottom-0 w-96 bg-card border-l border-border z-50 overflow-y-auto">
            <div className="p-6 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold">
                  {selectedUser ? "Информация о клиенте" : "Добавить клиента"}
                </h2>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Имя клиента
                  </label>
                  <input
                    ref={nameRef}
                    type="text"
                    defaultValue={selectedUser?.username || ""}
                    className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
                    placeholder="Меружан"
                    readOnly={!!selectedUser}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Telegram ID
                  </label>
                  <input
                    ref={tgRef}
                    type="text"
                    defaultValue={selectedUser?.telegramId || ""}
                    className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
                    placeholder="@username"
                    readOnly={!!selectedUser}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Шаблон тарифа</label>
                  <select
                    onChange={handleTemplateChange}
                    className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
                    disabled={!!selectedUser}
                  >
                    <option value="">Свой тариф</option>
                    {templates.map(t => (
                      <option key={t.id} value={t.id}>{t.name} — {t.dataLimitGb >= 999 ? "Безлимит" : `${t.dataLimitGb} ГБ`} — {t.price}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Группа</label>
                  <select
                    value={selectedUser?.groupId || selectedGroupId}
                    onChange={e => setSelectedGroupId(e.target.value)}
                    className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
                    disabled={!!selectedUser}
                  >
                    <option value="">Без группы</option>
                    {groups.map(g => (
                      <option key={g.id} value={g.id}>{g.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Протокол
                  </label>
                  <select
                    defaultValue="ShadeVPN"
                    className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
                  >
                    <option value="ShadeVPN">ShadeVPN (Native)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Лимит Трафика (ГБ)
                  </label>
                  <input
                    ref={limitRef}
                    type="number"
                    defaultValue={selectedUser?.dataLimit || 100}
                    className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
                    placeholder="100"
                    readOnly={!!selectedUser}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Дата окончания
                  </label>
                  <input
                    ref={dateRef}
                    type="date"
                    defaultValue={selectedUser?.subscriptionEnd || ""}
                    className="w-full px-3 py-2 bg-input rounded-lg border border-border focus:border-primary outline-none"
                    readOnly={!!selectedUser}
                  />
                </div>
              </div>

              {/* Ключ shade:// если просматриваем клиента */}
              {selectedUser && selectedUser.shadeLink && (
                <div className="pt-4 border-t border-border">
                  <label className="block text-sm font-semibold text-muted-foreground mb-2">КЛЮЧ ПОДКЛЮЧЕНИЯ</label>
                  <div className="p-3 rounded bg-muted/50 text-xs font-mono break-all">
                    {selectedUser.shadeLink}
                  </div>
                  <button
                    onClick={() => copyKey(selectedUser.shadeLink)}
                    className="mt-2 flex items-center gap-2 px-3 py-1.5 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors text-sm w-full justify-center"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    Скопировать ключ
                  </button>
                </div>
              )}

              <div className="flex gap-3 pt-4 border-t border-border">
                {!selectedUser ? (
                  <button
                    onClick={handleCreate}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                  >
                    {loading ? "Создание..." : "Создать клиента"}
                  </button>
                ) : (
                  <button
                    onClick={() => handleDelete(selectedUser.id)}
                    className="flex-1 px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors"
                  >
                    Удалить клиента
                  </button>
                )}
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="px-4 py-2 bg-muted text-foreground rounded-lg hover:bg-muted/80 transition-colors"
                >
                  Закрыть
                </button>
              </div>
            </div>
          </div>
        </>
      )}
      {/* QR Code Modal */}
      {qrModal?.isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <div className="w-full max-w-sm bg-[#1A1F2E] border border-border rounded-xl shadow-2xl p-6 relative">
            <button
              onClick={() => setQrModal(null)}
              className="absolute top-4 right-4 p-1.5 text-muted-foreground hover:bg-muted hover:text-white rounded-md transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            <h3 className="text-xl font-bold mb-6 pr-8">QR-Код для {qrModal.username}</h3>
            <div className="flex flex-col items-center gap-4 bg-white p-4 rounded-xl">
              <QRCodeSVG 
                value={qrModal.link} 
                size={280} 
                level={"M"} 
                includeMargin={true}
                className="rounded-lg"
              />
            </div>
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => { copyKey(qrModal.link); setQrModal(null); }}
                className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-md font-medium transition-colors"
                title="Скопировать ключ и закрыть"
              >
                <Copy className="w-4 h-4" /> Скопировать ключ
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
