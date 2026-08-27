const VARIANTS: Record<string, { label: string; color: string }> = {
  approved: { label: "APPROVED", color: "#1F6F54" },
  rejected: { label: "REJECTED", color: "#A6321C" },
  escalated: { label: "ESCALATED", color: "#B8843A" },
};

/**
 * The product's signature visual element. Every reviewed flag gets a decision
 * stamp — a deliberate reference to the physical rubber date-stamps used in
 * paper-based audit trails for decades. This ties the UI directly to the
 * product's core promise: human oversight + traceability, not a black box.
 */
export default function StampBadge({ decision }: { decision: string }) {
  const variant = VARIANTS[decision];
  if (!variant) return null;

  return (
    <div
      className="inline-flex items-center justify-center px-4 py-1.5 -rotate-2 select-none"
      style={{
        border: `2px solid ${variant.color}`,
        color: variant.color,
        boxShadow: `0 0 0 1px ${variant.color} inset`,
      }}
      role="status"
      aria-label={`Decision: ${variant.label.toLowerCase()}`}
    >
      <span className="font-display font-semibold tracking-[0.15em] text-sm">{variant.label}</span>
    </div>
  );
}
