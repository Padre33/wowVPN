// Единая точка конфигурации API
// На продакшене (сервер) — относительный путь через Nginx
// Для локальной разработки — прямой адрес сервера
export const API = import.meta.env.DEV
  ? "http://185.204.52.135:8000/api"
  : "/api";

const originalFetch = window.fetch;
window.fetch = async (input, init) => {
  init = init || {};
  init.headers = {
    ...init.headers,
    "X-Admin-Token": localStorage.getItem("adminToken") || "",
  };
  const response = await originalFetch(input, init);
  if (response.status === 401 && !window.location.href.includes("login")) {
    localStorage.removeItem("adminToken");
    window.location.reload();
  }
  return response;
};
