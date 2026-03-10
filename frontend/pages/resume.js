import Head from "next/head";
import Layout from "../components/Layout";
import { useState, useEffect } from "react";
import { api } from "../lib/api";

export default function ResumePage() {
    const [jobRole, setJobRole] = useState("");
    const [jobDesc, setJobDesc] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [resumes, setResumes] = useState([]);

    useEffect(() => {
        api.listResumes().then((r) => setResumes(r.resumes || [])).catch(() => { });
    }, []);

    async function handleGenerate() {
        if (!jobRole) { setError("Please enter a target job role."); return; }
        setError("");
        setLoading(true);
        setResult(null);
        try {
            const r = await api.generateResume({ job_role: jobRole, job_description: jobDesc });
            setResult(r);
            const updated = await api.listResumes();
            setResumes(updated.resumes || []);
        } catch (e) {
            setError(e.message || "Generation failed. Make sure the backend is running.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <>
            <Head>
                <title>Resume Builder — CareerForge</title>
                <meta name="description" content="AI-powered resume builder using Groq" />
            </Head>
            <div>
                <h1 className="page-title">Resume Builder</h1>
                <p className="page-sub">Generate a FAANG-level tailored resume using your GitHub projects + AI bullet points</p>

                <div className="grid-2" style={{ gap: "24px", alignItems: "start" }}>
                    {/* Left: Form */}
                    <div className="card">
                        <h2 className="section-title">✦ Generate New Resume</h2>

                        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                            <div className="form-group">
                                <label className="form-label">Target Role *</label>
                                <input
                                    id="job-role-input"
                                    className="input"
                                    placeholder="e.g. Backend Developer, SDE Intern, Full Stack Engineer"
                                    value={jobRole}
                                    onChange={(e) => setJobRole(e.target.value)}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Job Description (optional)</label>
                                <textarea
                                    id="job-desc-input"
                                    className="textarea"
                                    placeholder="Paste the job description here for a more tailored resume..."
                                    rows={6}
                                    value={jobDesc}
                                    onChange={(e) => setJobDesc(e.target.value)}
                                />
                                <span className="form-hint">AI will match your skills to the JD</span>
                            </div>

                            {error && <div className="alert alert-error">⚠ {error}</div>}

                            {result && (
                                <div className="alert alert-success">
                                    ✓ Resume generated!
                                    <a
                                        href={api.downloadUrl(result.resume_id)}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="btn btn-primary btn-sm"
                                        style={{ marginLeft: "12px" }}
                                    >
                                        ↓ Download DOCX
                                    </a>
                                </div>
                            )}

                            <button
                                id="generate-resume-btn"
                                className="btn btn-primary btn-lg"
                                onClick={handleGenerate}
                                disabled={loading}
                            >
                                {loading ? (
                                    <><span className="spinner" /> Generating with Groq AI...</>
                                ) : (
                                    <>✦ Generate Resume</>
                                )}
                            </button>

                            {loading && (
                                <div className="alert alert-info" style={{ fontSize: "0.8rem" }}>
                                    AI is writing resume bullets for your GitHub projects. This can take up to 30-60 seconds depending on network speed.
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: History */}
                    <div className="card">
                        <h2 className="section-title">📋 Generated Resumes</h2>
                        {resumes.length === 0 ? (
                            <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>
                                Your generated resumes will appear here.
                            </p>
                        ) : (
                            resumes.map((r) => (
                                <div key={r.id} className="resume-item">
                                    <div>
                                        <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                                            {r.job_role || "General"}
                                        </div>
                                        <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", marginTop: "2px" }}>
                                            {new Date(r.generated_at).toLocaleString()}
                                        </div>
                                    </div>
                                    <a
                                        className="btn btn-secondary btn-sm"
                                        href={api.downloadUrl(r.id)}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        ↓ Download
                                    </a>
                                </div>
                            ))
                        )}
                        <div className="divider" />
                        <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", lineHeight: 1.6 }}>
                            <strong style={{ color: "var(--text-secondary)" }}>💡 Tips:</strong><br />
                            • Import GitHub repos first for AI-generated bullets<br />
                            • Add job description for tailored keyword matching<br />
                            • Each resume is saved as a DOCX file you can edit
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

ResumePage.getLayout = (page) => <Layout>{page}</Layout>;
