import { useState } from "react";
import client from "../api/client";

export default function DecisionBar({ flagId, onDecided }: { flagId: string; onDecided: () => void }) {
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const decide = async (decision: "approved" | "rejected" | "escalated") => {
    if (decision === "escalated" && !comment.trim()) {
      setError("A comment is required when escalating a flag.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await client.post(`/flags/${flagId}/decision`, { decision, comment: comment || null });
      onDecided();
    } catch {
      setError("Could not record this decision. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-panel border border-line rounded-sm p-4">
      <label className="block text-xs font-medium text-ink-muted mb-1">
        Comment (required for escalation)
      </label>
      <textarea
        className="w-full border border-line rounded-sm px-3 py-2 text-sm mb-3 bg-panel text-ink placeholder:text-ink-faint focus:outline-none focus:border-ledger"
        rows={2}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      {error && <p className="text-stamp-red text-sm mb-3">{error}</p>}
      <div className="flex gap-2">
        <button
          disabled={submitting}
          onClick={() => decide("approved")}
          className="bg-ledger text-white text-sm font-medium px-4 py-2 rounded-sm disabled:opacity-40 hover:bg-ledger-dark transition-colors"
        >
          Approve
        </button>
        <button
          disabled={submitting}
          onClick={() => decide("rejected")}
          className="bg-line text-ink text-sm font-medium px-4 py-2 rounded-sm disabled:opacity-40 hover:bg-ink/20 transition-colors"
        >
          Reject
        </button>
        <button
          disabled={submitting}
          onClick={() => decide("escalated")}
          className="bg-stamp-red text-white text-sm font-medium px-4 py-2 rounded-sm disabled:opacity-40 hover:opacity-90 transition-colors"
        >
          Escalate
        </button>
      </div>
    </div>
  );
}
