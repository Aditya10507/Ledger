interface AuditEntry {
  id: string;
  action: string;
  actor: string;
  timestamp: string;
}

export default function AuditRow({ entry }: { entry: AuditEntry }) {
  return (
    <div className="bg-panel border border-line rounded-sm border-l-2 border-l-ledger pl-4 py-3">
      <p className="text-sm font-medium capitalize text-ink">
        {entry.action.replace(/_/g, " ")}
      </p>
      <p className="text-xs text-ink-faint font-mono mt-1">
        {entry.actor} · {new Date(entry.timestamp).toLocaleString()}
      </p>
    </div>
  );
}
