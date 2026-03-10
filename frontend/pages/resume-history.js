import Head from "next/head";
import Layout from "../components/Layout";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function ResumeHistoryPage() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    api.resumeHistory().then((r) => setItems(r.resumes || [])).catch(() => {});
  }, []);

  return (
    <>
      <Head><title>Resume History</title></Head>
      <div>
        <h1 className="page-title">Resume History</h1>
        <p className="page-sub">All generated resumes with stored generation configs.</p>
        <div className="card">
          {items.length === 0 ? <p style={{ color: "var(--text-muted)" }}>No generated resumes yet.</p> : items.map((r) => (
            <div key={r.id} className="resume-item">
              <div>
                <div style={{ fontWeight: 600 }}>{r.file_type.toUpperCase()} Resume #{r.id}</div>
                <div className="stat-sub">{new Date(r.created_at).toLocaleString()}</div>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={() => api.downloadDynamicResume(r.id)}>Download</button>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

ResumeHistoryPage.getLayout = (page) => <Layout>{page}</Layout>;
