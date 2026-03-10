import Head from "next/head";
import Layout from "../components/Layout";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function ResumeBuilderPage() {
  const [templates, setTemplates] = useState([]);
  const [profile, setProfile] = useState({ projects: [], internships: [], coding_platforms: [] });
  const [role, setRole] = useState("");
  const [skills, setSkills] = useState("");
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [selectedExp, setSelectedExp] = useState([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [templateId, setTemplateId] = useState("");
  const [outputType, setOutputType] = useState("docx");
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.listTemplates().then((r) => setTemplates(r.templates || [])).catch(() => {});
    api.getProfile().then((r) => setProfile(r)).catch(() => {});
  }, []);

  async function generate() {
    const payload = {
      template_id: templateId ? Number(templateId) : null,
      selected_projects: selectedProjects,
      selected_skills: skills.split(",").map((x) => x.trim()).filter(Boolean),
      selected_experience: selectedExp,
      selected_platforms: selectedPlatforms,
      target_role: role,
      output_type: outputType,
    };
    const res = await api.generateDynamicResume(payload);
    setResult(res);
  }

  return (
    <>
      <Head><title>Dynamic Resume Builder</title></Head>
      <div>
        <h1 className="page-title">Dynamic Resume Builder</h1>
        <p className="page-sub">Select specific data slices and generate tailored resumes per target role.</p>

        <div className="card" style={{ display: "grid", gap: 12 }}>
          <input className="input" placeholder="Target role" value={role} onChange={(e) => setRole(e.target.value)} />
          <input className="input" placeholder="Skills to highlight (comma separated)" value={skills} onChange={(e) => setSkills(e.target.value)} />
          <select className="select" value={templateId} onChange={(e) => setTemplateId(e.target.value)}>
            <option value="">No template</option>
            {templates.map((t) => <option key={t.template_id} value={t.template_id}>{t.template_name} ({t.template_type})</option>)}
          </select>
          <select className="select" value={outputType} onChange={(e) => setOutputType(e.target.value)}>
            <option value="docx">DOCX</option>
            <option value="pdf">PDF</option>
          </select>

          <div className="grid-3">
            <div>
              <div className="form-label">Projects</div>
              {(profile.projects || []).map((p) => (
                <label key={p.id} style={{ display: "block", marginBottom: 6 }}>
                  <input type="checkbox" onChange={(e) => setSelectedProjects(e.target.checked ? [...selectedProjects, p.id] : selectedProjects.filter((x) => x !== p.id))} /> {p.title}
                </label>
              ))}
            </div>
            <div>
              <div className="form-label">Experience</div>
              {(profile.internships || []).map((x) => (
                <label key={x.id} style={{ display: "block", marginBottom: 6 }}>
                  <input type="checkbox" onChange={(e) => setSelectedExp(e.target.checked ? [...selectedExp, x.id] : selectedExp.filter((id) => id !== x.id))} /> {x.role} @ {x.company}
                </label>
              ))}
            </div>
            <div>
              <div className="form-label">Platforms</div>
              {(profile.coding_platforms || []).map((x) => (
                <label key={x.id} style={{ display: "block", marginBottom: 6 }}>
                  <input type="checkbox" onChange={(e) => setSelectedPlatforms(e.target.checked ? [...selectedPlatforms, x.id] : selectedPlatforms.filter((id) => id !== x.id))} /> {x.platform_name}
                </label>
              ))}
            </div>
          </div>

          <button className="btn btn-primary" onClick={generate}>Generate Resume</button>

          {result && (
            <button className="btn btn-secondary" onClick={() => api.downloadDynamicResume(result.resume_id)}>
              Download Generated Resume
            </button>
          )}
        </div>
      </div>
    </>
  );
}

ResumeBuilderPage.getLayout = (page) => <Layout>{page}</Layout>;
