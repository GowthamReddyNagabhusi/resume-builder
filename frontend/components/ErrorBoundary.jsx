import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // Keep console output for debugging build/runtime errors.
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24 }}>
          <div style={{ maxWidth: 520, width: "100%", border: "1px solid #f2c7c7", background: "#fff7f7", borderRadius: 16, padding: 24 }}>
            <h2 style={{ marginTop: 0, marginBottom: 10 }}>Something went wrong</h2>
            <p style={{ marginTop: 0, marginBottom: 18, color: "#6b4b4b" }}>
              An unexpected error occurred. Please refresh the page.
            </p>
            <button className="btn btn-primary" onClick={() => window.location.reload()}>
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
