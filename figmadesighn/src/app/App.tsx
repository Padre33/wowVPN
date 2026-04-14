import { RouterProvider } from "react-router";
import { router } from "./routes";
import { useEffect } from "react";

export default function App() {
  useEffect(() => {
    document.documentElement.classList.add("dark");
  }, []);

  return <RouterProvider router={router} />;
}