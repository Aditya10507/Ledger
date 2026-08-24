import { useEffect, useState } from "react";
import client from "../api/client";
import AuditRow from "../components/AuditRow";

export default function AuditLog() {
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get("/audit-log")
      .then((res) => setEntries(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-xl font-semibold mb-6">Global Audit Log</h1>
      {loading ? (
        <p className="text-sm text-ink/60">Loading…</p>
      ) : entries.length === 0 ? (
        <p className="text-sm text-ink/60">No audit events yet.</p>
      ) : (
        entries.map((entry) => <AuditRow key={entry.id} entry={entry} />)
      )}
    </div>
  );
}
