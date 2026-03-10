import Head from "next/head";
import Layout from "../components/Layout";
import { useState, useEffect } from "react";
import { api } from "../lib/api";

const MODES = [
    { key: "prompt", label: "AI Chat", icon: "💬" },
    { key: "cover-letter", label: "Cover Letter", icon: "📝" },
    { key: "improve", label: "Improve Resume", icon: "⬆️" },
];

export default function AIPage() {
    const [mode, setMode] = useState("prompt");
    const [output, setOutput] = useState("");
    const [loading, setLoading] = useState(false);
    const [aiStatus, setAiStatus] = useState(null);

    // Chat
    const [prompt, setPrompt] = useState("");

    // Cover letter
    const [clRole, setClRole] = useState("");
    const [clComp, setClComp] = useState("");
    const [clJD, setClJD] = useState("");

    // Improve
    const [resumeText, setResumeText] = useState("");
    const [improveJD, setImproveJD] = useState("");

    useEffect(() => {
        api.aiStatus().then(setAiStatus).catch(() => { });
    }, []);

    const run = async () => {
        setLoading(true);
        setOutput("");
        try {
            let r;
            if (mode === "prompt") {
                r = await api.aiGenerate(prompt);
                setOutput(r.response || "No response.");
            } else if (mode === "cover-letter") {
                r = await api.aiCoverLetter({ job_role: clRole, company: clComp, job_description: clJD });
                setOutput(r.cover_letter || "No response.");
            } else if (mode === "improve") {
                r = await api.aiImprove({ resume_text: resumeText, job_description: improveJD });
                setOutput(r.suggestions || "No response.");
            }
        } catch (e) {
            setOutput(`Error: ${e.message || "Request failed. Check backend or Groq key."}`);
        }
        setLoading(false);
    };

    const isReady = () => {
        if (mode === "prompt") return prompt.trim().length > 0;
        if (mode === "cover-letter") return clRole && clComp;
        if (mode === "improve") return resumeText && improveJD;
        return false;
    };

    return (
        <>
            <Head>
                <title>AI Writer — CareerForge</title>
                <meta name="description" content="AI-powered cover letters, resume improvements, and career assistant" />
            </Head>
            <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "28px" }}>
                    <div>
                        <h1 className="page-title">AI Writer</h1>
                        <p className="page-sub">Powered by Groq for fast, professional writing assistance</p>
                    </div>
                    {aiStatus && (
                        <div style={{ display: "flex", gap: "8px" }}>
                            <span className={`badge ${aiStatus.groq?.available ? "badge-green" : "badge-gray"}`}>
                                {aiStatus.groq?.available ? `Groq Online · ${aiStatus.groq?.model || "model"}` : "Groq Offline"}
                            </span>
                            {aiStatus.groq?.available && <span className="badge badge-violet">AI Ready</span>}
                        </div>
                    )}
                </div>

                {/* Mode tabs */}
                <div style={{ display: "flex", gap: "8px", marginBottom: "24px" }}>
                    {MODES.map((m) => (
                        <button
                            key={m.key}
                            id={`mode-${m.key}`}
                            className={`btn ${mode === m.key ? "btn-primary" : "btn-secondary"}`}
                            onClick={() => { setMode(m.key); setOutput(""); }}
                        >
                            {m.icon} {m.label}
                        </button>
                    ))}
                </div>

                <div className="grid-2" style={{ gap: "24px", alignItems: "start" }}>
                    {/* Left: Input form */}
                    <div className="card">
                        {mode === "prompt" && (
                            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                                <h2 className="section-title">💬 Ask AI Anything</h2>
                                <div className="form-group">
                                    <label className="form-label">Your Prompt</label>
                                    <textarea
                                        id="ai-prompt-input"
                                        className="textarea"
                                        rows={8}
                                        placeholder={"How should I answer 'Tell me about yourself' for a backend role?\n\nWrite 5 DSA interview questions for Google SDE.\n\nHow can I improve my GitHub profile?"}
                                        value={prompt}
                                        onChange={(e) => setPrompt(e.target.value)}
                                    />
                                </div>
                            </div>
                        )}

                        {mode === "cover-letter" && (
                            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                                <h2 className="section-title">📝 Cover Letter Generator</h2>
                                <div className="form-group">
                                    <label className="form-label">Target Role *</label>
                                    <input id="cl-role-input" className="input" placeholder="Backend Developer, SDE Intern..." value={clRole} onChange={(e) => setClRole(e.target.value)} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Company *</label>
                                    <input id="cl-company-input" className="input" placeholder="Google, Flipkart, Zepto..." value={clComp} onChange={(e) => setClComp(e.target.value)} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Job Description</label>
                                    <textarea id="cl-jd-input" className="textarea" rows={5} placeholder="Paste the job description..." value={clJD} onChange={(e) => setClJD(e.target.value)} />
                                    <span className="form-hint">Results are much better with a JD</span>
                                </div>
                            </div>
                        )}

                        {mode === "improve" && (
                            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                                <h2 className="section-title">⬆️ Resume Improver</h2>
                                <div className="form-group">
                                    <label className="form-label">Your Resume Text *</label>
                                    <textarea id="resume-text-input" className="textarea" rows={6} placeholder="Paste your current resume content here..." value={resumeText} onChange={(e) => setResumeText(e.target.value)} />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Target Job Description *</label>
                                    <textarea id="improve-jd-input" className="textarea" rows={5} placeholder="Paste the job description to tailor suggestions..." value={improveJD} onChange={(e) => setImproveJD(e.target.value)} />
                                </div>
                            </div>
                        )}

                        <button
                            id="ai-run-btn"
                            className="btn btn-primary btn-lg"
                            style={{ width: "100%", marginTop: "16px" }}
                            onClick={run}
                            disabled={loading || !isReady()}
                        >
                            {loading ? <><span className="spinner" /> Generating...</> : "✦ Generate"}
                        </button>

                        {!aiStatus?.groq?.available && (
                            <div className="alert alert-info" style={{ marginTop: "12px", fontSize: "0.8rem" }}>
                                Groq is unavailable. Verify GROQ_API_KEY in your local environment.
                            </div>
                        )}
                    </div>

                    {/* Right: AI Output */}
                    <div className="card">
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                            <h2 className="section-title" style={{ marginBottom: 0 }}>AI Response</h2>
                            {output && (
                                <button
                                    className="btn btn-ghost btn-sm"
                                    onClick={() => navigator.clipboard.writeText(output)}
                                >
                                    📋 Copy
                                </button>
                            )}
                        </div>

                        {loading ? (
                            <div className={`ai-output generating`} style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                                <span className="spinner" />
                                <span style={{ color: "var(--text-secondary)" }}>
                                    AI is generating a response...
                                </span>
                            </div>
                        ) : output ? (
                            <div className="ai-output">{output}</div>
                        ) : (
                            <div className="ai-output" style={{ display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)" }}>
                                Your AI response will appear here
                            </div>
                        )}

                        {output && (
                            <div style={{ marginTop: "12px", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                                Generated by Groq
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}

AIPage.getLayout = (page) => <Layout>{page}</Layout>;
