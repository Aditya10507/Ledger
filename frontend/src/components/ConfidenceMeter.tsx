export default function ConfidenceMeter({ score }: { score: number }) {
  // Color communicates severity in addition to the number itself (never color alone — accessibility).
  const color = score >= 80 ? "text-critical" : score >= 50 ? "text-warning" : "text-success";
  return <span className={`text-sm font-mono font-medium ${color}`}>{score}/100</span>;
}
