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
      <p className="text-xs uppercase tracking-widest text-ink-muted mb-1">Administration</p>
      <h1 className="font-display text-2xl font-semibold text-ink mb-8">Global Audit Log</h1>
      {loading ? (
        <p className="text-sm text-ink-faint">Loading…</p>
      ) : entries.length === 0 ? (
        <div className="bg-panel border border-line rounded-sm p-8 text-center">
          <p className="text-sm text-ink-faint">No audit events yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {entries.map((entry) => (
            <AuditRow key={entry.id} entry={entry} />
          ))}
        </div>
      )}
    </div>
  );
}
