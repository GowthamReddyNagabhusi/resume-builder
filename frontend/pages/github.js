import Head from "next/head";
import Layout from "../components/Layout";
import { useState, useEffect } from "react";
import { api } from "../lib/api";

const LANG_COLORS = {
    Python: "#3572A5", JavaScript: "#f1e05a", "C++": "#f34b7d",
    Java: "#b07219", TypeScript: "#2b7489", Go: "#00ADD8",
    Rust: "#dea584", C: "#555555", "C#": "#178600", default: "var(--accent-blue)"
};

export default function GitHubPage() {
    const [username, setUsername] = useState("");
    const [projects, setProjects] = useState([]);
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(false);
    const [error, setError] = useState("");
    const [showAll, setShowAll] = useState(false);

    useEffect(() => {
        setFetching(true);
        api.listProjects(true).then((r) => {
            setProjects(r.projects || []);
        }).catch(() => { }).finally(() => setFetching(false));
    }, []);

    async function handleImport() {
        if (!username.trim()) { setError("Enter a GitHub username."); return; }
        setError(""); setLoading(true);
        try {
            const r = await api.importGitHub(username.trim());
            setProfile(r.profile);
            setProjects(r.projects || []);
        } catch (e) {
            setError(e.message || "Import failed. Check the username.");
        } finally {
            setLoading(false);
        }
    }

    async function handleToggle(id, current) {
        try {
            await api.toggleProject(id, !current);
            setProjects((p) => p.map((proj) => proj.id === id ? { ...proj, show_on_resume: current ? 0 : 1 } : proj));
        } catch { }
    }

    const displayed = showAll ? projects : projects.filter((p) => p.show_on_resume);

    return (
        <>
            <Head>
                <title>GitHub Import — CareerForge</title>
                <meta name="description" content="Import GitHub projects for resume auto-generation" />
            </Head>
            <div>
                <h1 className="page-title">GitHub Import</h1>
                <p className="page-sub">Fetch repos and choose which ones appear on your resume</p>

                {/* Import bar */}
                <div className="card" style={{ marginBottom: "24px" }}>
                    <div style={{ display: "flex", gap: "12px", alignItems: "flex-end" }}>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label className="form-label">GitHub Username</label>
                            <input
                                id="github-username-input"
                                className="input"
                                placeholder="e.g. GowthamReddyNagabhusi"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleImport()}
                            />
                        </div>
                        <button id="import-github-btn" className="btn btn-primary" onClick={handleImport} disabled={loading}>
                            {loading ? <><span className="spinner" /> Fetching...</> : "🐙 Import Repos"}
                        </button>
                    </div>
                    {error && <div className="alert alert-error" style={{ marginTop: "12px" }}>⚠ {error}</div>}
                </div>

                {/* GitHub profile card */}
                {profile && (
                    <div className="card" style={{ marginBottom: "24px" }}>
                        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
                            {profile.avatar_url && (
                                <img src={profile.avatar_url} alt={profile.username} style={{ width: 56, height: 56, borderRadius: "50%", border: "2px solid var(--glass-border)" }} />
                            )}
                            <div>
                                <div style={{ fontWeight: 700, fontSize: "1.1rem" }}>{profile.name || profile.username}</div>
                                <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "8px" }}>{profile.bio || ""}</div>
                                <div style={{ display: "flex", gap: "12px" }}>
                                    <span className="badge badge-blue">📁 {profile.public_repos} repos</span>
                                    <span className="badge badge-amber">⭐ {profile.total_stars} stars</span>
                                    <span className="badge badge-cyan">👥 {profile.followers} followers</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Project controls */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                    <h2 className="section-title" style={{ marginBottom: 0 }}>
                        {showAll ? "All Projects" : "Resume Projects"} ({displayed.length})
                    </h2>
                    <button className="btn btn-ghost btn-sm" onClick={() => setShowAll(!showAll)}>
                        {showAll ? "Show Resume Only" : "Show All"}
                    </button>
                </div>

                {fetching && <div className="loading-text"><span className="spinner" /> Loading projects...</div>}

                <div className="grid-2">
                    {displayed.map((proj) => (
                        <div key={proj.id} className="project-card">
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                <div style={{ flex: 1 }}>
                                    <div className="project-name">{proj.name}</div>
                                    <div className="project-desc">{proj.description || "No description"}</div>
                                </div>
                                <label className="toggle" style={{ marginLeft: "12px", flexShrink: 0 }}>
                                    <input
                                        type="checkbox"
                                        checked={!!proj.show_on_resume}
                                        onChange={() => handleToggle(proj.id, proj.show_on_resume)}
                                    />
                                    <span className="toggle-track" />
                                    <span className="toggle-thumb" />
                                </label>
                            </div>
                            <div className="project-meta">
                                {proj.language && proj.language !== "N/A" && (
                                    <span className="badge badge-blue" style={{ borderColor: (LANG_COLORS[proj.language] || LANG_COLORS.default) + "66", color: LANG_COLORS[proj.language] || LANG_COLORS.default }}>
                                        {proj.language}
                                    </span>
                                )}
                                {proj.stars > 0 && <span className="badge badge-amber">⭐ {proj.stars}</span>}
                                {proj.show_on_resume ? (
                                    <span className="badge badge-green">✓ On Resume</span>
                                ) : (
                                    <span className="badge badge-gray">Hidden</span>
                                )}
                            </div>
                            {proj.url && (
                                <a href={proj.url} target="_blank" rel="noreferrer"
                                    style={{ fontSize: "0.75rem", color: "var(--accent-blue)", marginTop: "8px", display: "block" }}>
                                    View on GitHub →
                                </a>
                            )}
                        </div>
                    ))}
                </div>

                {!fetching && displayed.length === 0 && (
                    <div className="card" style={{ textAlign: "center", padding: "40px" }}>
                        <div style={{ fontSize: "2rem", marginBottom: "12px" }}>🐙</div>
                        <p style={{ color: "var(--text-secondary)" }}>No projects found. Import a GitHub username above.</p>
                    </div>
                )}
            </div>
        </>
    );
}

GitHubPage.getLayout = (page) => <Layout>{page}</Layout>;
