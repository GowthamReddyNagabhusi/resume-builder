import Head from "next/head";
import { useState } from "react";
import { useRouter } from "next/router";
import { api } from "../lib/api";

export default function SignUpPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.signup({ name, email, password });
      router.push("/login");
    } catch (err) {
      setError(err.message || "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head><title>Signup</title></Head>
      <main className="main-content" style={{ marginLeft: 0, maxWidth: 520, margin: "40px auto" }}>
        <div className="card">
          <h1 className="page-title">Create Account</h1>
          <p className="page-sub">Set up your developer career profile once.</p>
          <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
            <input className="input" placeholder="Full Name" value={name} onChange={(e) => setName(e.target.value)} />
            <input className="input" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input className="input" type="password" placeholder="Password (8+ chars)" value={password} onChange={(e) => setPassword(e.target.value)} />
            {error && <div className="alert alert-error">{error}</div>}
            <button className="btn btn-primary" disabled={loading}>{loading ? "Creating..." : "Signup"}</button>
          </form>
          <div style={{ marginTop: 14, fontSize: "0.9rem" }}>
            Already registered? <a href="/login" style={{ color: "var(--accent-blue)" }}>Login</a>
          </div>
        </div>
      </main>
    </>
  );
}

SignUpPage.getLayout = (page) => page;
