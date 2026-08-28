export default function ConfidenceMeter({ score }: { score: number }) {
  const color =
    score >= 80 ? "text-stamp-red" : score >= 50 ? "text-stamp-amber" : "text-ledger";
  return (
    <span className={`text-sm font-mono font-medium ${color}`}>
      {score}/100
    </span>
  );
}
