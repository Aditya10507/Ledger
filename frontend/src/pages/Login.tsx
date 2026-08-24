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
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm p-8 w-full max-w-sm">
        <h1 className="text-xl font-semibold mb-1">Ledger</h1>
        <p className="text-sm text-ink/60 mb-6">AI Finance Controller</p>

        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          className="w-full border rounded-md px-3 py-2 mb-4 text-sm"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="block text-sm font-medium mb-1">Password</label>
        <input
          type="password"
          className="w-full border rounded-md px-3 py-2 mb-4 text-sm"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <p className="text-critical text-sm mb-4">{error}</p>}

        <button
          disabled={loading}
          className="w-full bg-primary text-white rounded-md py-2 text-sm font-medium disabled:opacity-50"
        >
          {loading ? "Logging in…" : "Log in"}
        </button>

        <p className="text-xs text-ink/40 mt-4">
          Demo: analyst@ledger.demo / password123 (pre-filled)
        </p>
      </form>
    </div>
  );
}
