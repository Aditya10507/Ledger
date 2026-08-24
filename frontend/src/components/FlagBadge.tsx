const LABELS: Record<string, string> = {
  duplicate: "Duplicate",
  missing_settlement: "Missing Settlement",
  amount_mismatch: "Amount Mismatch",
  timing_anomaly: "Timing Anomaly",
};

export default function FlagBadge({ type }: { type: string }) {
  return (
    <span className="text-xs font-medium bg-warning/10 text-warning px-2 py-1 rounded-full whitespace-nowrap">
      {LABELS[type] ?? type}
    </span>
  );
}
