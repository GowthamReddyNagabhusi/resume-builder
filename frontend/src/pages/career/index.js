import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/lib/context/AuthContext';
import { apiClient } from '@/lib/api/client';

const TABS = ['Education', 'Experience', 'Skills', 'Projects', 'Certifications'];

// ── small shared components ──────────────────────────────────────────────────

function SectionHeader({ title, onAdd }) {
  return (
    <div className="flex justify-between items-center mb-4">
      <h2 className="text-xl font-semibold">{title}</h2>
      <button
        onClick={onAdd}
        className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        + Add
      </button>
    </div>
  );
}

function DeleteButton({ onClick }) {
  return (
    <button onClick={onClick} className="text-red-500 hover:text-red-700 text-sm">
      Delete
    </button>
  );
}

function FormModal({ title, fields, onSubmit, onClose }) {
  const [values, setValues] = useState({});
  const [saving, setSaving] = useState(false);
  const handleChange = (e) => setValues((v) => ({ ...v, [e.target.name]: e.target.value }));
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try { await onSubmit(values); onClose(); }
    catch { /* bubble errors to parent */ }
    finally { setSaving(false); }
  };
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          {fields.map(({ name, label, type = 'text', required }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              {type === 'textarea' ? (
                <textarea
                  name={name}
                  required={required}
                  rows={3}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  onChange={handleChange}
                />
              ) : (
                <input
                  name={name}
                  type={type}
                  required={required}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  onChange={handleChange}
                />
              )}
            </div>
          ))}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── tab content components ────────────────────────────────────────────────────

function EducationTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getEducation().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);
  const handleAdd = async (values) => { await apiClient.createEducation(values); load(); };
  const handleDelete = async (id) => { await apiClient.deleteEducation(id); load(); };
  return (
    <>
      <SectionHeader title="Education" onAdd={() => setModal(true)} />
      {items.length === 0 && <p className="text-gray-400 text-sm">No education entries yet.</p>}
      <ul className="divide-y divide-gray-100">
        {items.map((ed) => (
          <li key={ed.id} className="py-3 flex justify-between">
            <div>
              <p className="font-medium">{ed.degree} — {ed.institution}</p>
              <p className="text-sm text-gray-500">{ed.field_of_study} · {ed.start_year}–{ed.end_year || 'Present'}</p>
            </div>
            <DeleteButton onClick={() => handleDelete(ed.id)} />
          </li>
        ))}
      </ul>
      {modal && (
        <FormModal
          title="Add Education"
          onClose={() => setModal(false)}
          onSubmit={handleAdd}
          fields={[
            { name: 'institution', label: 'Institution', required: true },
            { name: 'degree', label: 'Degree', required: true },
            { name: 'field_of_study', label: 'Field of Study' },
            { name: 'start_year', label: 'Start Year', type: 'number' },
            { name: 'end_year', label: 'End Year (blank if current)', type: 'number' },
            { name: 'gpa', label: 'GPA' },
            { name: 'description', label: 'Notes', type: 'textarea' },
          ]}
        />
      )}
    </>
  );
}

function ExperienceTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getExperience().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);
  const handleAdd = async (values) => { await apiClient.createExperience(values); load(); };
  const handleDelete = async (id) => { await apiClient.deleteExperience(id); load(); };
  return (
    <>
      <SectionHeader title="Work Experience" onAdd={() => setModal(true)} />
      {items.length === 0 && <p className="text-gray-400 text-sm">No experience entries yet.</p>}
      <ul className="divide-y divide-gray-100">
        {items.map((ex) => (
          <li key={ex.id} className="py-3 flex justify-between">
            <div>
              <p className="font-medium">{ex.position} at {ex.company}</p>
              <p className="text-sm text-gray-500">{ex.start_date} – {ex.end_date || 'Present'}</p>
              {ex.description && <p className="text-sm text-gray-600 mt-1 line-clamp-2">{ex.description}</p>}
            </div>
            <DeleteButton onClick={() => handleDelete(ex.id)} />
          </li>
        ))}
      </ul>
      {modal && (
        <FormModal
          title="Add Experience"
          onClose={() => setModal(false)}
          onSubmit={handleAdd}
          fields={[
            { name: 'company', label: 'Company', required: true },
            { name: 'position', label: 'Position / Title', required: true },
            { name: 'location', label: 'Location' },
            { name: 'start_date', label: 'Start Date (YYYY-MM)', required: true },
            { name: 'end_date', label: 'End Date (blank if current)' },
            { name: 'description', label: 'Description / Achievements', type: 'textarea' },
          ]}
        />
      )}
    </>
  );
}

function SkillsTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getSkills().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);
  const handleAdd = async (values) => { await apiClient.createSkill(values); load(); };
  const handleDelete = async (id) => { await apiClient.deleteSkill(id); load(); };
  return (
    <>
      <SectionHeader title="Skills" onAdd={() => setModal(true)} />
      {items.length === 0 && <p className="text-gray-400 text-sm">No skills added yet.</p>}
      <div className="flex flex-wrap gap-2 mt-2">
        {items.map((sk) => (
          <span key={sk.id} className="flex items-center gap-1 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm">
            {sk.name}
            <button onClick={() => handleDelete(sk.id)} className="ml-1 text-blue-400 hover:text-red-500">×</button>
          </span>
        ))}
      </div>
      {modal && (
        <FormModal
          title="Add Skill"
          onClose={() => setModal(false)}
          onSubmit={handleAdd}
          fields={[
            { name: 'name', label: 'Skill name', required: true },
            { name: 'proficiency', label: 'Proficiency (e.g. Beginner / Intermediate / Expert)' },
            { name: 'category', label: 'Category (e.g. Programming, Design)' },
          ]}
        />
      )}
    </>
  );
}

function ProjectsTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getProjects().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);
  const handleAdd = async (values) => { await apiClient.createProject(values); load(); };
  const handleDelete = async (id) => { await apiClient.deleteProject(id); load(); };
  return (
    <>
      <SectionHeader title="Projects" onAdd={() => setModal(true)} />
      {items.length === 0 && <p className="text-gray-400 text-sm">No projects added yet.</p>}
      <ul className="divide-y divide-gray-100">
        {items.map((pr) => (
          <li key={pr.id} className="py-3 flex justify-between">
            <div>
              <p className="font-medium">{pr.name}</p>
              {pr.description && <p className="text-sm text-gray-500 line-clamp-2">{pr.description}</p>}
              {pr.url && <a href={pr.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline">{pr.url}</a>}
            </div>
            <DeleteButton onClick={() => handleDelete(pr.id)} />
          </li>
        ))}
      </ul>
      {modal && (
        <FormModal
          title="Add Project"
          onClose={() => setModal(false)}
          onSubmit={handleAdd}
          fields={[
            { name: 'name', label: 'Project Name', required: true },
            { name: 'description', label: 'Description', type: 'textarea' },
            { name: 'technologies', label: 'Technologies (comma-separated)' },
            { name: 'url', label: 'URL (optional)' },
            { name: 'start_date', label: 'Start Date' },
            { name: 'end_date', label: 'End Date' },
          ]}
        />
      )}
    </>
  );
}

function CertificationsTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getCertifications().then(setItems).catch(() => {});
  useEffect(() => { load(); }, []);
  const handleAdd = async (values) => { await apiClient.createCertification(values); load(); };
  return (
    <>
      <SectionHeader title="Certifications" onAdd={() => setModal(true)} />
      {items.length === 0 && <p className="text-gray-400 text-sm">No certifications added yet.</p>}
      <ul className="divide-y divide-gray-100">
        {items.map((cert) => (
          <li key={cert.id} className="py-3">
            <p className="font-medium">{cert.name}</p>
            <p className="text-sm text-gray-500">{cert.issuing_organization} · {cert.issue_date}</p>
          </li>
        ))}
      </ul>
      {modal && (
        <FormModal
          title="Add Certification"
          onClose={() => setModal(false)}
          onSubmit={handleAdd}
          fields={[
            { name: 'name', label: 'Certification Name', required: true },
            { name: 'issuing_organization', label: 'Issued By', required: true },
            { name: 'issue_date', label: 'Issue Date (YYYY-MM-DD)' },
            { name: 'expiry_date', label: 'Expiry Date (leave blank if none)' },
            { name: 'credential_id', label: 'Credential ID' },
            { name: 'credential_url', label: 'Credential URL' },
          ]}
        />
      )}
    </>
  );
}

const TAB_COMPONENTS = {
  Education: EducationTab,
  Experience: ExperienceTab,
  Skills: SkillsTab,
  Projects: ProjectsTab,
  Certifications: CertificationsTab,
};

// ── Page ─────────────────────────────────────────────────────────────────────

export default function CareerPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('Education');

  useEffect(() => {
    if (!loading && !user) router.replace('/auth/login');
  }, [user, loading, router]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><p className="text-gray-500">Loading…</p></div>;
  }

  const TabContent = TAB_COMPONENTS[activeTab];

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-bold text-blue-600">ResumeBuilder.AI</Link>
          <Link href="/dashboard" className="text-sm text-gray-600 hover:text-blue-600">← Dashboard</Link>
        </div>
      </nav>

      <main className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">My Career Data</h1>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <TabContent />
        </div>
      </main>
    </div>
  );
}
