import { Navigate, Outlet } from "react-router-dom";

/**
 * Previously there was no route protection at all — visiting /dashboard while
 * logged out would fire API calls that failed with 401 and rely on the axios
 * interceptor to redirect. This guards routes before any request is made.
 */
export default function RequireAuth() {
  const token = localStorage.getItem("ledger_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}
