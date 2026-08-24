interface AuditEntry {
  id: string;
  action: string;
  actor: string;
  timestamp: string;
}

export default function AuditRow({ entry }: { entry: AuditEntry }) {
  return (
    <div className="border-l-2 border-ink/10 pl-4 py-2 text-sm">
      <p className="font-medium capitalize">{entry.action.replace(/_/g, " ")}</p>
      <p className="text-xs text-ink/50">
        {entry.actor} · {new Date(entry.timestamp).toLocaleString()}
      </p>
    </div>
  );
}
