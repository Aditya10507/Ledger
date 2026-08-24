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
    <div className="bg-white rounded-lg p-4">
      <label className="block text-xs font-medium text-ink/60 mb-1">
        Comment (required for escalation)
      </label>
      <textarea
        className="w-full border rounded-md px-3 py-2 text-sm mb-3"
        rows={2}
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      {error && <p className="text-critical text-sm mb-3">{error}</p>}
      <div className="flex gap-2">
        <button
          disabled={submitting}
          onClick={() => decide("approved")}
          className="bg-success text-white text-sm font-medium px-4 py-2 rounded-md disabled:opacity-40"
        >
          Approve
        </button>
        <button
          disabled={submitting}
          onClick={() => decide("rejected")}
          className="bg-ink/10 text-ink text-sm font-medium px-4 py-2 rounded-md disabled:opacity-40"
        >
          Reject
        </button>
        <button
          disabled={submitting}
          onClick={() => decide("escalated")}
          className="bg-critical text-white text-sm font-medium px-4 py-2 rounded-md disabled:opacity-40"
        >
          Escalate
        </button>
      </div>
    </div>
  );
}
