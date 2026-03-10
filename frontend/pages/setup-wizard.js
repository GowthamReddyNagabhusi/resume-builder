import Head from "next/head";
import Layout from "../components/Layout";
import { useState } from "react";
import { useRouter } from "next/router";
import { api } from "../lib/api";

function emptyEducation() {
  return { university: "", degree: "", branch: "", cgpa: "", start_year: "", end_year: "" };
}

const PLATFORM_CATALOG = [
  { name: "LeetCode", icon: "LC", baseUrl: "https://leetcode.com/" },
  { name: "Codeforces", icon: "CF", baseUrl: "https://codeforces.com/profile/" },
  { name: "CodeChef", icon: "CC", baseUrl: "https://www.codechef.com/users/" },
  { name: "AtCoder", icon: "AC", baseUrl: "https://atcoder.jp/users/" },
  { name: "GeeksForGeeks", icon: "GFG", baseUrl: "https://www.geeksforgeeks.org/user/" },
  { name: "HackerRank", icon: "HR", baseUrl: "https://www.hackerrank.com/profile/" },
  { name: "HackerEarth", icon: "HE", baseUrl: "https://www.hackerearth.com/@/" },
];

function makeInitialConnections() {
  const out = {};
  for (const p of PLATFORM_CATALOG) {
    out[p.name] = { connected: false, username: "" };
  }
  return out;
}

export default function SetupWizardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const [personal, setPersonal] = useState({
    full_name: "", email: "", phone: "", location: "", linkedin: "", portfolio: "", github_username: "",
  });
  const [education, setEducation] = useState([emptyEducation()]);
  const [platforms, setPlatforms] = useState(makeInitialConnections());

  const codingPlatforms = PLATFORM_CATALOG
    .filter((p) => platforms[p.name]?.connected && (platforms[p.name]?.username || "").trim())
    .map((p) => ({
      platform_name: p.name,
      username: platforms[p.name].username.trim(),
      profile_link: `${p.baseUrl}${platforms[p.name].username.trim()}`,
    }));

  async function saveAll() {
    setLoading(true);
    setMessage("");
    try {
      await api.saveSetup({
        personal_details: {
          ...personal,
          github_profile: personal.github_username ? `https://github.com/${personal.github_username.trim()}` : "",
        },
        education: education.filter((x) => x.university || x.degree),
        coding_platforms: codingPlatforms,
        projects: [],
        internships: [],
        certifications: [],
        training: [],
      });
      router.push("/dashboard");
    } catch (e) {
      setMessage(e.message || "Failed to save setup");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head><title>Career Setup Wizard</title></Head>
      <div>
        <h1 className="page-title">Career Setup Wizard</h1>
        <p className="page-sub">Complete your structured profile once, then generate role-specific resumes instantly.</p>

        <div className="card" style={{ marginBottom: 18 }}>
          <h2 className="section-title">Personal Details</h2>
          <div className="grid-2">
            {Object.keys(personal).map((k) => (
              <input
                key={k}
                className="input"
                placeholder={k.replaceAll("_", " ")}
                value={personal[k]}
                onChange={(e) => setPersonal({ ...personal, [k]: e.target.value })}
              />
            ))}
          </div>
        </div>

        <div className="card" style={{ marginBottom: 18 }}>
          <h2 className="section-title">Education</h2>
          {education.map((e, idx) => (
            <div key={idx} className="grid-3" style={{ marginBottom: 10 }}>
              <input className="input" placeholder="University" value={e.university} onChange={(v) => {
                const copy = [...education]; copy[idx].university = v.target.value; setEducation(copy);
              }} />
              <input className="input" placeholder="Degree" value={e.degree} onChange={(v) => {
                const copy = [...education]; copy[idx].degree = v.target.value; setEducation(copy);
              }} />
              <input className="input" placeholder="Branch" value={e.branch} onChange={(v) => {
                const copy = [...education]; copy[idx].branch = v.target.value; setEducation(copy);
              }} />
            </div>
          ))}
          <button className="btn btn-secondary btn-sm" onClick={() => setEducation([...education, emptyEducation()])}>+ Add education</button>
        </div>

        <div className="card" style={{ marginBottom: 18 }}>
          <h2 className="section-title">Connect Coding Platforms</h2>
          <p className="form-hint" style={{ marginBottom: 12 }}>
            Connect by username. Profile links are created automatically.
          </p>

          <div className="platform-grid">
            {PLATFORM_CATALOG.map((p) => {
              const state = platforms[p.name];
              return (
                <div key={p.name} className={`platform-card ${state.connected ? "connected" : ""}`}>
                  <div className="platform-head">
                    <div className="platform-icon">{p.icon}</div>
                    <div>
                      <div className="platform-name">{p.name}</div>
                      <div className="platform-state">{state.connected ? "Connected" : "Not Connected"}</div>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                    <input
                      className="input"
                      placeholder={`${p.name} username`}
                      value={state.username}
                      onChange={(e) => setPlatforms({
                        ...platforms,
                        [p.name]: { ...state, username: e.target.value },
                      })}
                    />
                    <button
                      className={`btn btn-sm ${state.connected ? "btn-secondary" : "btn-primary"}`}
                      onClick={() => setPlatforms({
                        ...platforms,
                        [p.name]: { ...state, connected: !state.connected },
                      })}
                    >
                      {state.connected ? "Disconnect" : "Connect"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {message && <div className="alert alert-error" style={{ marginBottom: 12 }}>{message}</div>}
        <button className="btn btn-primary" onClick={saveAll} disabled={loading}>{loading ? "Saving..." : "Complete Setup"}</button>
      </div>
    </>
  );
}

SetupWizardPage.getLayout = (page) => <Layout>{page}</Layout>;
