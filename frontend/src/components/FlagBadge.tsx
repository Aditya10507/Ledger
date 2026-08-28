const LABELS: Record<string, string> = {
  duplicate: "Duplicate",
  missing_settlement: "Missing Settlement",
  amount_mismatch: "Amount Mismatch",
  timing_anomaly: "Timing Anomaly",
};

export default function FlagBadge({ type }: { type: string }) {
  return (
    <span className="text-xs font-medium bg-stamp-amber-light text-stamp-amber px-2.5 py-1 rounded-sm whitespace-nowrap">
      {LABELS[type] ?? type}
    </span>
  );
}
