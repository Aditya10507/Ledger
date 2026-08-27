import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="max-w-md mx-auto p-8 text-center mt-24">
      <p className="font-display text-4xl font-semibold text-ink mb-2">404</p>
      <p className="text-sm text-ink-muted mb-6">This page doesn't exist.</p>
      <Link to="/dashboard" className="text-ledger text-sm font-medium underline hover:text-ledger-dark">
        Back to Dashboard
      </Link>
    </div>
  );
}
