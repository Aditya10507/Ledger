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
      <h1 className="text-xl font-semibold mb-6">Flags</h1>

      {loading ? (
        <p className="text-sm text-ink/60">Loading…</p>
      ) : flags.length === 0 ? (
        <p className="text-sm text-ink/60">No anomalies found — all transactions reconciled cleanly.</p>
      ) : (
        <div className="space-y-2">
          {flags.map((flag) => (
            <Link
              to={`/flags/${flag.id}`}
              key={flag.id}
              className="flex items-center justify-between bg-white rounded-md px-4 py-3 hover:shadow-sm transition-shadow"
            >
              <FlagBadge type={flag.flag_type} />
              <ConfidenceMeter score={flag.confidence_score} />
              <span className="text-sm capitalize text-ink/60">{flag.status}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
