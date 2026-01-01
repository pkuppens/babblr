import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCcw, Copy, Check } from "lucide-react";
import "./ErrorBoundary.css";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  copied: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    copied: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, copied: false };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  private copyToClipboard = () => {
    if (this.state.error) {
      navigator.clipboard.writeText(
        this.state.error.stack || this.state.error.message
      );
      this.setState({ copied: true });
      setTimeout(() => this.setState({ copied: false }), 2000);
    }
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary-container">
          <div className="error-card">
            <div className="error-icon">
              <AlertTriangle size={48} color="#ef4444" />
            </div>
            <h1>Something went wrong</h1>
            <p>
              We've encountered an unexpected error. Don't worry, your data is
              safe.
            </p>

            <div className="error-details">
              <pre>{this.state.error?.message}</pre>
            </div>

            <div className="error-actions">
              <button onClick={this.handleReset} className="btn-primary">
                <RefreshCcw size={18} />
                Refresh Page
              </button>
              <button onClick={this.copyToClipboard} className="btn-secondary">
                {this.state.copied ? <Check size={18} /> : <Copy size={18} />}
                {this.state.copied ? "Copied!" : "Copy Error Text"}
              </button>
            </div>

            <p className="support-hint">
              If the problem persists, please contact support and include the
              error text.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
