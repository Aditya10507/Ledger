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
        <h1 className="text-xl font-semibold">Reconciliation Runs</h1>
        <Link to="/runs/new" className="bg-primary text-white rounded-md px-4 py-2 text-sm font-medium">
          New Run
        </Link>
      </div>

      {loading ? (
        <p className="text-sm text-ink/60">Loading…</p>
      ) : runs.length === 0 ? (
        <div className="bg-white rounded-lg p-8 text-center">
          <p className="text-sm text-ink/60 mb-4">No runs yet.</p>
          <Link to="/runs/new" className="text-primary text-sm font-medium underline">
            Start your first reconciliation
          </Link>
        </div>
      ) : (
        <table className="w-full text-sm bg-white rounded-lg overflow-hidden">
          <thead className="bg-ink/5 text-left">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Matched</th>
              <th className="px-4 py-3">Flagged</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id} className="border-t">
                <td className="px-4 py-3">{new Date(run.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3 capitalize">{run.status}</td>
                <td className="px-4 py-3">
                  {run.matched_count} / {run.total_records}
                </td>
                <td className="px-4 py-3">
                  <Link to={`/runs/${run.id}`} className="text-primary underline">
                    {run.flagged_count} flags
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
