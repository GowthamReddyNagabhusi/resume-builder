import Head from "next/head";
import { useState } from "react";
import { useRouter } from "next/router";
import { api, setToken } from "../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.login({ email, password });
      setToken(res.access_token);
      if (res.user?.setup_completed) {
        router.push("/dashboard");
      } else {
        router.push("/setup-wizard");
      }
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head><title>Login</title></Head>
      <main className="main-content" style={{ marginLeft: 0, maxWidth: 520, margin: "40px auto" }}>
        <div className="card">
          <h1 className="page-title">Login</h1>
          <p className="page-sub">Access your developer career profile.</p>
          <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
            <input className="input" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input className="input" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            {error && <div className="alert alert-error">{error}</div>}
            <button className="btn btn-primary" disabled={loading}>{loading ? "Signing in..." : "Login"}</button>
          </form>
          <div style={{ marginTop: 14, fontSize: "0.9rem" }}>
            New here? <a href="/signup" style={{ color: "var(--accent-blue)" }}>Create account</a>
          </div>
        </div>
      </main>
    </>
  );
}

LoginPage.getLayout = (page) => page;
