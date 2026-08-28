import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

interface Run {
  id: string;
  status: string;
  matched_count: number;
  flagged_count: number;
  total_records: number;
  created_at: string;
}

export default function Dashboard() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get("/reconciliation/runs")
      .then((res) => setRuns(res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-xs uppercase tracking-widest text-ink-muted mb-1">
            Overview
          </p>
          <h1 className="font-display text-2xl font-semibold text-ink">
            Reconciliation Runs
          </h1>
        </div>
        <Link
          to="/runs/new"
          className="bg-ledger text-white rounded-sm px-5 py-2.5 text-sm font-medium hover:bg-ledger-dark transition-colors"
        >
          New Run
        </Link>
      </div>

      {loading ? (
        <p className="text-sm text-ink-faint">Loading…</p>
      ) : runs.length === 0 ? (
        <div className="bg-panel border border-line rounded-sm p-8 text-center">
          <p className="text-sm text-ink-faint mb-4">No runs yet.</p>
          <Link
            to="/runs/new"
            className="text-ledger text-sm font-medium underline hover:text-ledger-dark"
          >
            Start your first reconciliation
          </Link>
        </div>
      ) : (
        <div className="bg-panel border border-line rounded-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-paper border-b border-line">
              <tr>
                <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-ink-muted font-medium">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-ink-muted font-medium">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-ink-muted font-medium">
                  Matched
                </th>
                <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-ink-muted font-medium">
                  Flagged
                </th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id} className="border-b border-line last:border-0 hover:bg-paper/50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-ink-muted">
                    {new Date(run.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 capitalize text-ink">{run.status}</td>
                  <td className="px-4 py-3 font-mono text-xs">
                    {run.matched_count} / {run.total_records}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      to={`/runs/${run.id}`}
                      className="text-ledger font-medium hover:text-ledger-dark transition-colors"
                    >
                      {run.flagged_count} flags
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
