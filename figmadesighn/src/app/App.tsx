import { RouterProvider } from "react-router";
import { router } from "./routes";
import { useEffect, useState } from "react";
import { Login } from "./pages/Login";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("adminToken"));

  useEffect(() => {
    document.documentElement.classList.add("dark");
  }, []);

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return <RouterProvider router={router} />;
}