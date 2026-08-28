import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import client from "../api/client";
import ConfidenceMeter from "../components/ConfidenceMeter";
import FlagBadge from "../components/FlagBadge";

export default function FlagList() {
  const { runId } = useParams();
  const [flags, setFlags] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get(`/reconciliation/runs/${runId}/flags`)
      .then((res) => setFlags(res.data))
      .finally(() => setLoading(false));
  }, [runId]);

  return (
    <div className="max-w-4xl mx-auto p-8">
      <p className="text-xs uppercase tracking-widest text-ink-muted mb-1">Reconciliation Run</p>
      <h1 className="font-display text-2xl font-semibold text-ink mb-8">Flags</h1>

      {loading ? (
        <p className="text-sm text-ink-faint">Loading…</p>
      ) : flags.length === 0 ? (
        <div className="bg-panel border border-line rounded-sm p-8 text-center">
          <p className="text-sm text-ink-faint">No anomalies found — all transactions reconciled cleanly.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {flags.map((flag) => (
            <Link
              to={`/flags/${flag.id}`}
              key={flag.id}
              className="flex items-center justify-between bg-panel border border-line rounded-sm px-4 py-3 hover:border-ledger/50 transition-colors"
            >
              <FlagBadge type={flag.flag_type} />
              <ConfidenceMeter score={flag.confidence_score} />
              <span className="text-sm capitalize text-ink-muted">{flag.status}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
