export default function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-panel border border-line rounded-sm p-4">
      <p className="text-2xl font-semibold font-mono text-ink">{value}</p>
      <p className="text-xs text-ink-faint mt-1 uppercase tracking-wide">{label}</p>
    </div>
  );
}
