import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";

export default function Login() {
  const [email, setEmail] = useState("analyst@ledger.demo");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await client.post("/auth/login", { email, password });
      localStorage.setItem("ledger_token", data.access_token);
      localStorage.setItem("ledger_role", data.role);
      navigate("/dashboard");
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper">
      <form
        onSubmit={handleSubmit}
        className="bg-panel border border-line rounded-sm shadow-sm p-8 w-full max-w-sm"
      >
        <div className="mb-6">
          <h1 className="font-display text-2xl font-semibold text-ink tracking-tight">
            Ledger
          </h1>
          <p className="font-mono text-[10px] uppercase tracking-widest text-ink-faint mt-1">
            AI Finance Controller
          </p>
        </div>

        <label htmlFor="login-email" className="block text-xs font-medium text-ink-muted mb-1">
          Email
        </label>
        <input
          id="login-email"
          type="email"
          autoComplete="email"
          className="w-full border border-line rounded-sm px-3 py-2 mb-4 text-sm bg-panel text-ink placeholder:text-ink-faint focus:outline-none focus:border-ledger"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label htmlFor="login-password" className="block text-xs font-medium text-ink-muted mb-1">
          Password
        </label>
        <input
          id="login-password"
          type="password"
          autoComplete="current-password"
          className="w-full border border-line rounded-sm px-3 py-2 mb-4 text-sm bg-panel text-ink placeholder:text-ink-faint focus:outline-none focus:border-ledger"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && (
          <p role="alert" className="text-stamp-red text-sm mb-4">
            {error}
          </p>
        )}

        <button
          disabled={loading}
          className="w-full bg-ledger text-white rounded-sm py-2.5 text-sm font-medium disabled:opacity-50 hover:bg-ledger-dark transition-colors"
        >
          {loading ? "Logging in…" : "Log in"}
        </button>

        <p className="text-xs text-ink-faint mt-4">
          Demo: analyst@ledger.demo / password123 (pre-filled)
        </p>
      </form>
    </div>
  );
}
