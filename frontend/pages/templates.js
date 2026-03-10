import Head from "next/head";
import Layout from "../components/Layout";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function TemplatesPage() {
  const [items, setItems] = useState([]);
  const [msg, setMsg] = useState("");

  async function load() {
    const res = await api.listTemplates();
    setItems(res.templates || []);
  }

  useEffect(() => { load().catch(() => {}); }, []);

  async function onUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setMsg("");
    try {
      await api.uploadTemplate(file);
      setMsg("Uploaded successfully");
      await load();
    } catch (err) {
      setMsg(err.message || "Upload failed");
    }
  }

  return (
    <>
      <Head><title>Templates</title></Head>
      <div>
        <h1 className="page-title">Resume Templates</h1>
        <p className="page-sub">Upload DOCX, LaTeX, or JSON templates for dynamic generation.</p>

        <div className="card" style={{ marginBottom: 16 }}>
          <input type="file" className="input" onChange={onUpload} />
          {msg && <div className="alert alert-info" style={{ marginTop: 10 }}>{msg}</div>}
        </div>

        <div className="card">
          <h2 className="section-title">My Templates</h2>
          {items.length === 0 ? <p style={{ color: "var(--text-muted)" }}>No templates uploaded yet.</p> : items.map((t) => (
            <div key={t.template_id} className="resume-item">
              <div>
                <div>{t.template_name}</div>
                <div className="stat-sub">{t.template_type} • {new Date(t.created_at).toLocaleString()}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

TemplatesPage.getLayout = (page) => <Layout>{page}</Layout>;
