import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { Users } from "./pages/Users";
import { Groups } from "./pages/Groups";
import { ConfigProfiles } from "./pages/ConfigProfiles";
import { Nodes } from "./pages/Nodes";
import { Templates } from "./pages/Templates";
import { ResponseRules } from "./pages/ResponseRules";
import { HWIDInspector } from "./pages/HWIDInspector";
import { ConnectionLogs } from "./pages/ConnectionLogs";
import { Settings } from "./pages/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Home },
      { path: "users", Component: Users },
      { path: "groups", Component: Groups },
      { path: "config-profiles", Component: ConfigProfiles },
      { path: "nodes", Component: Nodes },
      { path: "templates", Component: Templates },
      { path: "response-rules", Component: ResponseRules },
      { path: "hwid-inspector", Component: HWIDInspector },
      { path: "connection-logs", Component: ConnectionLogs },
      { path: "settings", Component: Settings },
    ],
  },
]);
