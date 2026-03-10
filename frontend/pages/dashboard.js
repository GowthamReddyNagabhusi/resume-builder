import Head from "next/head";
import Layout from "../components/Layout";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { api } from "../lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    api.me().then((res) => {
      setUser(res.user);
      if (!res.user?.setup_completed) {
        router.push("/setup-wizard");
      }
    }).catch(() => router.push("/login"));

    api.getProfile().then((res) => setProfile(res.profile || null)).catch(() => {});
    api.resumeHistory().then((res) => setResumes(res.resumes || [])).catch(() => {});
  }, [router]);

  const completionScore = profile?.setup_completed ? 100 : 35;
  const latestResume = resumes[0];

  async function handleSync() {
    setSyncing(true);
    try {
      await api.syncPlatforms();
    } catch (_) {
      // no-op
    } finally {
      setSyncing(false);
    }
  }

  return (
    <>
      <Head><title>Dashboard — CareerForge</title></Head>
      <div className="dashboard-shell">
        <section className="dashboard-hero">
          <div>
            <h1 className="page-title">Welcome back, {user?.name?.split(" ")[0] || "Developer"}</h1>
            <p className="page-sub">Your career intelligence workspace for profile growth, tailored resumes, and delivery tracking.</p>
          </div>
          <div className="hero-actions">
            <a className="btn btn-primary" href="/resume-builder">Build Resume</a>
            <button className="btn btn-secondary" onClick={handleSync} disabled={syncing}>
              {syncing ? "Syncing..." : "Sync Platforms"}
            </button>
          </div>
        </section>

        <section className="grid-3">
          <div className="stat-card stat-accent-blue">
            <div className="stat-label">Profile Completion</div>
            <div className="stat-value">{completionScore}%</div>
            <div className="stat-sub">{profile?.setup_completed ? "All onboarding sections completed" : "Complete setup wizard for best results"}</div>
          </div>
          <div className="stat-card stat-accent-emerald">
            <div className="stat-label">Generated Resumes</div>
            <div className="stat-value">{resumes.length}</div>
            <div className="stat-sub">Dynamic role-specific versions</div>
          </div>
          <div className="stat-card stat-accent-slate">
            <div className="stat-label">Account</div>
            <div className="stat-value" style={{ fontSize: "1.15rem" }}>{user?.name || "-"}</div>
            <div className="stat-sub">{user?.email || ""}</div>
          </div>
        </section>

        <section className="grid-2" style={{ marginTop: 18 }}>
          <div className="card panel-elevated">
            <h2 className="section-title">Execution Center</h2>
            <div className="dashboard-link-list">
              <a className="dashboard-link-row" href="/setup-wizard">
                <span>Career Setup Wizard</span>
                <span>{profile?.setup_completed ? "Update" : "Complete"}</span>
              </a>
              <a className="dashboard-link-row" href="/templates">
                <span>Template Library</span>
                <span>Manage</span>
              </a>
              <a className="dashboard-link-row" href="/resume-history">
                <span>Resume History</span>
                <span>Review</span>
              </a>
              <a className="dashboard-link-row" href="/jobs">
                <span>Job Tracker</span>
                <span>Track</span>
              </a>
            </div>
          </div>

          <div className="card panel-elevated">
            <h2 className="section-title">Latest Artifact</h2>
            {latestResume ? (
              <div>
                <p style={{ color: "var(--text-secondary)", marginBottom: 12 }}>
                  Last generated resume is ready for download.
                </p>
                <div className="resume-item" style={{ paddingTop: 4 }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>Resume #{latestResume.id}</div>
                    <div className="stat-sub">{new Date(latestResume.created_at).toLocaleString()}</div>
                  </div>
                  <button className="btn btn-secondary btn-sm" onClick={() => api.downloadDynamicResume(latestResume.id)}>
                    Download
                  </button>
                </div>
              </div>
            ) : (
              <p style={{ color: "var(--text-muted)" }}>No resume generated yet. Start from Resume Builder.</p>
            )}
          </div>
        </section>

        <section className="card panel-elevated" style={{ marginTop: 18 }}>
          <h2 className="section-title">Professional Snapshot</h2>
          <div className="grid-3">
            <div>
              <div className="stat-label">LinkedIn</div>
              <div className="stat-sub" style={{ marginTop: 6 }}>{profile?.linkedin || "Not added"}</div>
            </div>
            <div>
              <div className="stat-label">Portfolio</div>
              <div className="stat-sub" style={{ marginTop: 6 }}>{profile?.portfolio || "Not added"}</div>
            </div>
            <div>
              <div className="stat-label">Location</div>
              <div className="stat-sub" style={{ marginTop: 6 }}>{profile?.location || "Not added"}</div>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}

DashboardPage.getLayout = (page) => <Layout>{page}</Layout>;
