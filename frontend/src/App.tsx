import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AuditLog from "./pages/AuditLog";
import Dashboard from "./pages/Dashboard";
import FlagDetail from "./pages/FlagDetail";
import FlagList from "./pages/FlagList";
import Login from "./pages/Login";
import RunSummary from "./pages/RunSummary";
import UploadRun from "./pages/UploadRun";
import NotFound from "./pages/NotFound";
import RequireAuth from "./components/RequireAuth";
import Layout from "./components/Layout";
import ErrorBoundary from "./components/ErrorBoundary";

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Protected routes — require JWT token + sidebar layout */}
          <Route element={<RequireAuth />}>
            <Route element={<Layout />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/runs/new" element={<UploadRun />} />
              <Route path="/runs/:runId" element={<RunSummary />} />
              <Route path="/runs/:runId/flags" element={<FlagList />} />
              <Route path="/flags/:flagId" element={<FlagDetail />} />
              <Route path="/audit-log" element={<AuditLog />} />
            </Route>
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
