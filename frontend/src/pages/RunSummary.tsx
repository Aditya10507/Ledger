import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import client from "../api/client";
import StatCard from "../components/StatCard";

export default function RunSummary() {
  const { runId } = useParams();
  const [run, setRun] = useState<any>(null);

  useEffect(() => {
    client.get(`/reconciliation/runs/${runId}`).then((res) => setRun(res.data));
  }, [runId]);

  if (!run) return <div className="p-8 text-sm text-ink/60">Loading…</div>;

  const matchRate = run.total_records ? Math.round((run.matched_count / run.total_records) * 100) : 0;

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-xl font-semibold mb-6">Run Summary</h1>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Records" value={run.total_records} />
        <StatCard label="Matched" value={`${matchRate}%`} />
        <StatCard label="Flagged" value={run.flagged_count} />
        <StatCard label="Flagged Value" value={`₹${run.total_flagged_value ?? 0}`} />
      </div>

      <Link to={`/runs/${runId}/flags`} className="bg-primary text-white rounded-md px-4 py-2 text-sm font-medium">
        View Flags
      </Link>
    </div>
  );
}
