import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error("Ledger UI crashed:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-paper flex items-center justify-center">
          <div className="max-w-sm text-center">
            <p className="font-display text-2xl font-semibold text-ink mb-2">Something went wrong.</p>
            <p className="text-sm text-ink-muted mb-6">
              Please refresh the page. If this keeps happening, contact your admin.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-ledger text-white text-sm font-medium px-5 py-2.5 rounded-sm hover:bg-ledger-dark transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
