import Head from "next/head";
import Layout from "../components/Layout";
import { useState, useEffect } from "react";
import { api } from "../lib/api";

const COLUMNS = [
    { key: "applied", label: "Applied", color: "var(--accent-blue)", icon: "📤" },
    { key: "interview", label: "Interview", color: "var(--accent-violet)", icon: "🎙️" },
    { key: "offer", label: "Offer", color: "var(--accent-green)", icon: "🎉" },
    { key: "rejected", label: "Rejected", color: "var(--accent-rose)", icon: "✗" },
];

function JobCard({ job, onMove, onDelete }) {
    const moves = COLUMNS.filter((c) => c.key !== job.status);
    return (
        <div className="job-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                    <div className="job-company">{job.company}</div>
                    <div className="job-role">{job.role}</div>
                    <div className="job-date">{job.applied_at ? new Date(job.applied_at).toLocaleDateString() : ""}</div>
                    {job.notes && (
                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "6px" }}>
                            {job.notes}
                        </div>
                    )}
                    {job.link && (
                        <a href={job.link} target="_blank" rel="noreferrer" style={{ fontSize: "0.72rem", color: "var(--accent-blue)", display: "block", marginTop: "4px" }}>
                            View Posting →
                        </a>
                    )}
                </div>
                <button onClick={() => onDelete(job.id)} className="btn btn-ghost btn-sm" style={{ padding: "2px 6px", fontSize: "0.7rem", color: "var(--text-muted)" }}>✕</button>
            </div>
            <div style={{ display: "flex", gap: "4px", marginTop: "10px", flexWrap: "wrap" }}>
                {moves.map((col) => (
                    <button
                        key={col.key}
                        onClick={() => onMove(job.id, col.key)}
                        className="btn btn-ghost btn-sm"
                        style={{ fontSize: "0.7rem", padding: "3px 8px", color: col.color, borderColor: col.color + "44" }}
                    >
                        → {col.label}
                    </button>
                ))}
            </div>
        </div>
    );
}

export default function JobsPage() {
    const [kanban, setKanban] = useState({ applied: [], interview: [], offer: [], rejected: [] });
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ company: "", role: "", link: "", notes: "" });
    const [submitting, setSubmitting] = useState(false);

    const load = async () => {
        try {
            const r = await api.listJobs();
            setKanban(r.kanban || { applied: [], interview: [], offer: [], rejected: [] });
            setTotal(r.total || 0);
        } catch { }
        setLoading(false);
    };

    useEffect(() => { load(); }, []);

    const handleAdd = async () => {
        if (!form.company || !form.role) return;
        setSubmitting(true);
        try {
            await api.createJob(form);
            setForm({ company: "", role: "", link: "", notes: "" });
            setShowForm(false);
            await load();
        } catch { }
        setSubmitting(false);
    };

    const handleMove = async (id, status) => {
        try {
            await api.updateJob(id, { status });
            await load();
        } catch { }
    };

    const handleDelete = async (id) => {
        try {
            await api.deleteJob(id);
            await load();
        } catch { }
    };

    return (
        <>
            <Head>
                <title>Job Tracker — CareerForge</title>
                <meta name="description" content="Track job applications with Kanban board" />
            </Head>
            <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "28px" }}>
                    <div>
                        <h1 className="page-title">Job Tracker</h1>
                        <p className="page-sub">{total} applications tracked · Move between stages as you progress</p>
                    </div>
                    <button id="add-job-btn" className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                        {showForm ? "✕ Cancel" : "+ Add Application"}
                    </button>
                </div>

                {/* Add form */}
                {showForm && (
                    <div className="card" style={{ marginBottom: "24px" }}>
                        <h2 className="section-title">New Application</h2>
                        <div className="grid-2" style={{ gap: "12px" }}>
                            <div className="form-group">
                                <label className="form-label">Company *</label>
                                <input id="job-company-input" className="input" placeholder="Google, Amazon, Flipkart..." value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Role *</label>
                                <input id="job-role-input" className="input" placeholder="SDE Intern, Backend Developer..." value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Job Link</label>
                                <input id="job-link-input" className="input" placeholder="https://careers.google.com/..." value={form.link} onChange={(e) => setForm({ ...form, link: e.target.value })} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Notes</label>
                                <input id="job-notes-input" className="input" placeholder="Referral, applied via LinkedIn..." value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
                            </div>
                        </div>
                        <div style={{ marginTop: "16px", display: "flex", gap: "10px" }}>
                            <button id="submit-job-btn" className="btn btn-primary" onClick={handleAdd} disabled={submitting || !form.company || !form.role}>
                                {submitting ? <><span className="spinner" /> Adding...</> : "Add Application"}
                            </button>
                            <button className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
                        </div>
                    </div>
                )}

                {/* Kanban board */}
                {loading ? (
                    <div className="loading-text"><span className="spinner" /> Loading applications...</div>
                ) : (
                    <div className="kanban">
                        {COLUMNS.map((col) => (
                            <div key={col.key} className="kanban-col">
                                <div className="kanban-header">
                                    <span className="kanban-title" style={{ color: col.color }}>
                                        {col.icon} {col.label}
                                    </span>
                                    <span className="kanban-count">{(kanban[col.key] || []).length}</span>
                                </div>
                                {(kanban[col.key] || []).length === 0 ? (
                                    <div style={{ textAlign: "center", padding: "24px 0", color: "var(--text-muted)", fontSize: "0.8rem" }}>
                                        Empty
                                    </div>
                                ) : (
                                    (kanban[col.key] || []).map((job) => (
                                        <JobCard key={job.id} job={job} onMove={handleMove} onDelete={handleDelete} />
                                    ))
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
}

JobsPage.getLayout = (page) => <Layout>{page}</Layout>;
