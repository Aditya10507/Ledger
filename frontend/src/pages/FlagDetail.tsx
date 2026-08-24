import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import client from "../api/client";
import AuditRow from "../components/AuditRow";
import ConfidenceMeter from "../components/ConfidenceMeter";
import DecisionBar from "../components/DecisionBar";
import FlagBadge from "../components/FlagBadge";

export default function FlagDetail() {
  const { flagId } = useParams();
  const [flag, setFlag] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);

  const load = () => {
    if (!flagId) return;
    client.get(`/flags/${flagId}`).then((res) => setFlag(res.data));
    client.get(`/flags/${flagId}/audit-trail`).then((res) => setAudit(res.data));
  };

  useEffect(load, [flagId]);

  if (!flag) return <div className="p-8 text-sm text-ink/60">Loading…</div>;

  return (
    <div className="max-w-3xl mx-auto p-8">
      <div className="flex items-center gap-3 mb-4">
        <FlagBadge type={flag.flag_type} />
        <ConfidenceMeter score={flag.confidence_score} />
        <span className="text-sm capitalize text-ink/60">{flag.status}</span>
      </div>

      <div className="bg-white rounded-lg p-6 mb-6">
        <h2 className="text-sm font-medium text-ink/60 mb-2">AI Explanation</h2>
        <p className="text-sm">
          {flag.explanation_status === "ok"
            ? flag.ai_explanation
            : "AI explanation unavailable — reviewed using computed data."}
        </p>
        {flag.computed_delta != null && (
          <p className="text-xs text-ink/50 mt-3 font-mono">Computed delta: {flag.computed_delta}</p>
        )}
      </div>

      {flag.status === "open" ? (
        <DecisionBar flagId={flag.id} onDecided={load} />
      ) : (
        <div className="bg-white rounded-lg p-4 text-sm">
          <p className="capitalize font-medium">{flag.status}</p>
          {flag.review_comment && <p className="text-ink/60 mt-1">"{flag.review_comment}"</p>}
        </div>
      )}

      <div className="mt-8">
        <h2 className="text-sm font-medium text-ink/60 mb-2">Audit Trail</h2>
        {audit.map((entry) => (
          <AuditRow key={entry.id} entry={entry} />
        ))}
      </div>
    </div>
  );
}
