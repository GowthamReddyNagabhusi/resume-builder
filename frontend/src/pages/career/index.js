import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/lib/context/AuthContext';
import { apiClient } from '@/lib/api/client';

const TABS = ['Education', 'Experience', 'Skills', 'Projects', 'Certifications', 'Achievements', 'Profiles'];

const TAB_ICONS = {
  Education: '🎓', Experience: '💼', Skills: '⚡', Projects: '🚀',
  Certifications: '🏆', Achievements: '🏅', Profiles: '🔗',
};

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/career', label: 'Career Data', icon: '📝' },
  { href: '/resume/generate', label: 'Generate', icon: '✨' },
  { href: '/resume', label: 'My Resumes', icon: '📄' },
];

const MONTHS = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const GRADE_TYPES = ['CGPA', 'GPA', 'Percentage', 'Marks'];

const PLATFORM_OPTIONS = [
  { value: 'github', label: 'GitHub', icon: '🐙' },
  { value: 'linkedin', label: 'LinkedIn', icon: '💼' },
  { value: 'leetcode', label: 'LeetCode', icon: '🧩' },
  { value: 'codeforces', label: 'Codeforces', icon: '⚔️' },
  { value: 'hackerrank', label: 'HackerRank', icon: '💚' },
  { value: 'codechef', label: 'CodeChef', icon: '👨‍🍳' },
  { value: 'portfolio', label: 'Portfolio', icon: '🌐' },
  { value: 'twitter', label: 'Twitter / X', icon: '🐦' },
  { value: 'kaggle', label: 'Kaggle', icon: '📊' },
  { value: 'other', label: 'Other', icon: '🔗' },
];

// ── Modal ────────────────────────────────────────────────────────

function FormModal({ title, fields, onSubmit, onClose, children }) {
  const [values, setValues] = useState({});
  const [saving, setSaving] = useState(false);
  const handleChange = (e) => setValues((v) => ({ ...v, [e.target.name]: e.target.value }));
  const handleToggle = (name) => setValues((v) => ({ ...v, [name]: v[name] ? false : true }));
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try { await onSubmit(values); onClose(); }
    catch { /* errors handled by parent */ }
    finally { setSaving(false); }
  };

  return (
    <div className="fixed inset-0 bg-surface-900/95 backdrop-blur-md flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="glass-card w-full max-w-lg p-6 animate-scale-in border border-white/[0.15] shadow-2xl shadow-black/40">
        <h3 className="text-lg font-semibold text-white mb-5">{title}</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          {fields.map(({ name, label, type = 'text', required, options }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-surface-300 mb-1">{label}</label>
              {type === 'textarea' ? (
                <textarea
                  name={name} required={required} rows={3}
                  className="textarea-premium" onChange={handleChange}
                />
              ) : type === 'select' ? (
                <select
                  name={name} required={required}
                  className="input-premium bg-surface-800"
                  onChange={handleChange} defaultValue=""
                >
                  <option value="" disabled>Select…</option>
                  {(options || []).map((opt) => (
                    <option key={opt.value || opt} value={opt.value || opt}>{opt.label || opt}</option>
                  ))}
                </select>
              ) : type === 'toggle' ? (
                <button
                  type="button"
                  onClick={() => handleToggle(name)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${values[name] ? 'bg-brand-500' : 'bg-surface-700'}`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${values[name] ? 'translate-x-6' : 'translate-x-1'}`} />
                </button>
              ) : (
                <input
                  name={name} type={type} required={required}
                  className="input-premium" onChange={handleChange}
                />
              )}
            </div>
          ))}
          {children}
          <div className="flex justify-end gap-3 pt-3">
            <button type="button" onClick={onClose} className="btn-ghost text-sm">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary text-sm !py-2 !px-4">
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Tab content ──────────────────────────────────────────────────

function SectionHeader({ title, onAdd }) {
  return (
    <div className="flex justify-between items-center mb-5">
      <h2 className="section-heading">{title}</h2>
      <button onClick={onAdd} className="btn-primary text-sm !py-2 !px-4">+ Add</button>
    </div>
  );
}

function ItemCard({ children, onDelete }) {
  return (
    <div className="glass-card p-4 flex justify-between items-start group animate-slide-up">
      <div className="flex-1 min-w-0">{children}</div>
      {onDelete && (
        <button onClick={onDelete} className="btn-danger text-xs opacity-0 group-hover:opacity-100 transition-opacity ml-3 shrink-0">
          Delete
        </button>
      )}
    </div>
  );
}

function EmptyState({ message }) {
  return <p className="text-surface-500 text-sm text-center py-8">{message}</p>;
}

function EducationTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getEducation().then(setItems).catch(() => { });
  useEffect(() => { load(); }, []);

  const gradeLabel = (item) => {
    const type = item.grade_type || 'CGPA';
    const val = item.cgpa;
    if (!val) return '';
    return `${type}: ${val}`;
  };

  return (
    <>
      <SectionHeader title="Education" onAdd={() => setModal(true)} />
      {items.length === 0 && <EmptyState message="No education entries yet. Click + Add to get started." />}
      <div className="space-y-3">
        {items.map((ed) => (
          <ItemCard key={ed.id} onDelete={() => { apiClient.deleteEducation(ed.id).then(load); }}>
            <p className="font-medium text-white">{ed.degree || ed.university} — {ed.university || ed.degree}</p>
            <p className="text-sm text-surface-400">
              {ed.branch}
              {ed.start_month ? ` · ${ed.start_month}` : ''} {ed.start_year || ''}
              {' – '}
              {ed.is_current ? (
                <span className="text-emerald-400 font-medium">Currently studying</span>
              ) : (
                <>{ed.end_month ? `${ed.end_month} ` : ''}{ed.end_year || 'Present'}</>
              )}
            </p>
            {ed.cgpa && <p className="text-xs text-brand-400 mt-1">{gradeLabel(ed)}</p>}
          </ItemCard>
        ))}
      </div>
      {modal && (
        <FormModal title="Add Education" onClose={() => setModal(false)} onSubmit={async (v) => { await apiClient.createEducation(v); load(); }} fields={[
          { name: 'institution', label: 'Institution', required: true },
          { name: 'degree', label: 'Degree', required: true },
          { name: 'field_of_study', label: 'Field of Study' },
          { name: 'start_month', label: 'Start Month', type: 'select', options: MONTHS.filter(Boolean).map(m => ({ value: m, label: m })) },
          { name: 'start_year', label: 'Start Year', type: 'number' },
          { name: 'is_current', label: 'Currently Studying', type: 'toggle' },
          { name: 'end_month', label: 'End Month', type: 'select', options: MONTHS.filter(Boolean).map(m => ({ value: m, label: m })) },
          { name: 'end_year', label: 'End Year', type: 'number' },
          { name: 'grade_type', label: 'Grade Type', type: 'select', options: GRADE_TYPES.map(g => ({ value: g, label: g })) },
          { name: 'gpa', label: 'Grade Value' },
        ]} />
      )}
    </>
  );
}

function ExperienceTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getExperience().then(setItems).catch(() => { });
  useEffect(() => { load(); }, []);
  return (
    <>
      <SectionHeader title="Work Experience" onAdd={() => setModal(true)} />
      {items.length === 0 && <EmptyState message="No experience entries yet. Click + Add to get started." />}
      <div className="space-y-3">
        {items.map((ex) => (
          <ItemCard key={ex.id} onDelete={() => { apiClient.deleteExperience(ex.id).then(load); }}>
            <p className="font-medium text-white">{ex.role || ex.position} at {ex.company}</p>
            <p className="text-sm text-surface-400">{ex.start_date} – {ex.end_date || 'Present'}</p>
            {ex.description && <p className="text-sm text-surface-500 mt-1 line-clamp-2">{ex.description}</p>}
          </ItemCard>
        ))}
      </div>
      {modal && (
        <FormModal title="Add Experience" onClose={() => setModal(false)} onSubmit={async (v) => { await apiClient.createExperience(v); load(); }} fields={[
          { name: 'company', label: 'Company', required: true },
          { name: 'position', label: 'Position / Title', required: true },
          { name: 'start_date', label: 'Start Date (YYYY-MM)', required: true },
          { name: 'end_date', label: 'End Date (blank if current)' },
          { name: 'description', label: 'Description', type: 'textarea' },
        ]} />
      )}
    </>
  );
}

function SkillsTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getSkills().then(setItems).catch(() => { });
  useEffect(() => { load(); }, []);
  return (
    <>
      <SectionHeader title="Skills" onAdd={() => setModal(true)} />
      {items.length === 0 && <EmptyState message="No skills added yet. Click + Add to get started." />}
      <div className="flex flex-wrap gap-2">
        {items.map((sk) => (
          <span key={sk.id} className="badge group cursor-default">
            {sk.name}
            <button onClick={() => { apiClient.deleteSkill(sk.id).then(load); }} className="ml-1.5 text-brand-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity">×</button>
          </span>
        ))}
      </div>
      {modal && (
        <FormModal title="Add Skill" onClose={() => setModal(false)} onSubmit={async (v) => { await apiClient.createSkill(v); load(); }} fields={[
          { name: 'name', label: 'Skill Name', required: true },
          { name: 'proficiency', label: 'Proficiency (Beginner / Intermediate / Expert)' },
          { name: 'category', label: 'Category (Programming, Design, etc.)' },
        ]} />
      )}
    </>
  );
}

function ProjectsTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getProjects().then(setItems).catch(() => { });
  useEffect(() => { load(); }, []);
  return (
    <>
      <SectionHeader title="Projects" onAdd={() => setModal(true)} />
      {items.length === 0 && <EmptyState message="No projects added yet. Click + Add to get started." />}
      <div className="space-y-3">
        {items.map((pr) => (
          <ItemCard key={pr.id} onDelete={() => { apiClient.deleteProject(pr.id).then(load); }}>
            <p className="font-medium text-white">{pr.title || pr.name}</p>
            {pr.description && <p className="text-sm text-surface-400 mt-1 line-clamp-2">{pr.description}</p>}
            {(pr.tech_stack || pr.technologies) && <p className="text-xs text-brand-400 mt-1">{pr.tech_stack || pr.technologies}</p>}
          </ItemCard>
        ))}
      </div>
      {modal && (
        <FormModal title="Add Project" onClose={() => setModal(false)} onSubmit={async (v) => { await apiClient.createProject(v); load(); }} fields={[
          { name: 'name', label: 'Project Name', required: true },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'technologies', label: 'Technologies (comma-separated)' },
          { name: 'url', label: 'URL (optional)' },
        ]} />
      )}
    </>
  );
}

function CertificationsTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getCertifications().then(setItems).catch(() => { });
  useEffect(() => { load(); }, []);
  return (
    <>
      <SectionHeader title="Certifications" onAdd={() => setModal(true)} />
      {items.length === 0 && <EmptyState message="No certifications added yet. Click + Add to get started." />}
      <div className="space-y-3">
        {items.map((cert) => (
          <ItemCard key={cert.id} onDelete={() => { apiClient.deleteCertification(cert.id).then(load); }}>
            <p className="font-medium text-white">{cert.certificate_name || cert.name}</p>
            <p className="text-sm text-surface-400">{cert.provider || cert.issuing_organization} · {cert.issue_date}</p>
          </ItemCard>
        ))}
      </div>
      {modal && (
        <FormModal title="Add Certification" onClose={() => setModal(false)} onSubmit={async (v) => { await apiClient.createCertification(v); load(); }} fields={[
          { name: 'name', label: 'Certification Name', required: true },
          { name: 'issuing_organization', label: 'Issued By', required: true },
          { name: 'issue_date', label: 'Issue Date (YYYY-MM-DD)' },
          { name: 'credential_url', label: 'Credential URL' },
        ]} />
      )}
    </>
  );
}

function AchievementsTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getAchievements().then(setItems).catch(() => { });
  useEffect(() => { load(); }, []);
  return (
    <>
      <SectionHeader title="Achievements" onAdd={() => setModal(true)} />
      {items.length === 0 && <EmptyState message="No achievements added yet. Click + Add to get started." />}
      <div className="space-y-3">
        {items.map((ach) => (
          <ItemCard key={ach.id} onDelete={() => { apiClient.deleteAchievement(ach.id).then(load); }}>
            <p className="font-medium text-white">{ach.title}</p>
            {ach.organization && <p className="text-sm text-surface-400">{ach.organization}{ach.date ? ` · ${ach.date}` : ''}</p>}
            {ach.description && <p className="text-sm text-surface-500 mt-1 line-clamp-2">{ach.description}</p>}
            {ach.link && <a href={ach.link} target="_blank" rel="noopener noreferrer" className="text-xs text-brand-400 hover:text-brand-300 mt-1 inline-block">🔗 View</a>}
          </ItemCard>
        ))}
      </div>
      {modal && (
        <FormModal title="Add Achievement" onClose={() => setModal(false)} onSubmit={async (v) => { await apiClient.createAchievement(v); load(); }} fields={[
          { name: 'title', label: 'Title', required: true },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'organization', label: 'Organization / Event' },
          { name: 'date', label: 'Date (YYYY-MM-DD)' },
          { name: 'link', label: 'Link (optional)' },
        ]} />
      )}
    </>
  );
}

function ProfilesTab() {
  const [items, setItems] = useState([]);
  const [modal, setModal] = useState(false);
  const load = () => apiClient.getPlatforms().then(setItems).catch(() => { });
  useEffect(() => { load(); }, []);

  const getPlatformInfo = (platformValue) => {
    return PLATFORM_OPTIONS.find(p => p.value === platformValue) || { value: platformValue, label: platformValue, icon: '🔗' };
  };

  return (
    <>
      <SectionHeader title="Platform Profiles" onAdd={() => setModal(true)} />
      {items.length === 0 && <EmptyState message="No platform profiles added yet. Click + Add to connect your accounts." />}
      <div className="space-y-3">
        {items.map((link) => {
          const info = getPlatformInfo(link.platform);
          return (
            <ItemCard key={link.id} onDelete={() => { apiClient.deletePlatform(link.id).then(load); }}>
              <div className="flex items-center gap-3">
                <span className="text-2xl">{info.icon}</span>
                <div>
                  <p className="font-medium text-white">{info.label}</p>
                  <p className="text-sm text-surface-400">{link.username || ''}</p>
                  {link.profile_url && (
                    <a href={link.profile_url} target="_blank" rel="noopener noreferrer" className="text-xs text-brand-400 hover:text-brand-300">
                      {link.profile_url}
                    </a>
                  )}
                </div>
              </div>
            </ItemCard>
          );
        })}
      </div>
      {modal && (
        <FormModal title="Add Platform Profile" onClose={() => setModal(false)} onSubmit={async (v) => { await apiClient.createPlatform(v); load(); }} fields={[
          { name: 'platform', label: 'Platform', required: true, type: 'select', options: PLATFORM_OPTIONS },
          { name: 'username', label: 'Username / Handle' },
          { name: 'profile_url', label: 'Profile URL' },
        ]} />
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
  Achievements: AchievementsTab,
  Profiles: ProfilesTab,
};

// ── Page ────────────────────────────────────────────────────────

export default function CareerPage() {
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('Education');

  useEffect(() => {
    if (!loading && !user) router.replace('/auth/login');
  }, [user, loading, router]);

  if (loading) {
    return <div className="min-h-screen bg-surface-950 flex items-center justify-center"><div className="spinner spinner-lg" /></div>;
  }

  const TabContent = TAB_COMPONENTS[activeTab];

  return (
    <div className="min-h-screen bg-surface-950 flex">
      {/* Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 border-r border-white/[0.06] p-4">
        <div className="flex items-center gap-2 px-3 mb-8">
          <div className="w-8 h-8 rounded-lg bg-accent-gradient flex items-center justify-center text-white font-bold text-sm shadow-glow">CF</div>
          <span className="text-lg font-bold text-white">CareerForge</span>
        </div>
        <nav className="flex-1 space-y-1">
          {NAV_ITEMS.map(({ href, label, icon }) => (
            <Link key={href} href={href} className={href === '/career' ? 'nav-link-active flex items-center gap-3' : 'nav-link flex items-center gap-3'}>
              <span>{icon}</span>{label}
            </Link>
          ))}
        </nav>
        <button onClick={() => { logout(); router.push('/'); }} className="btn-ghost text-sm text-surface-500 w-full text-left flex items-center gap-3">
          <span>🚪</span>Sign Out
        </button>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        <div className="lg:hidden border-b border-white/[0.06] p-4 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-accent-gradient flex items-center justify-center text-white font-bold text-xs">CF</div>
            <span className="font-bold text-white">CareerForge</span>
          </Link>
          <div className="flex gap-1">
            {NAV_ITEMS.filter(n => n.href !== '/career').map(({ href, icon }) => (
              <Link key={href} href={href} className="btn-ghost !px-2">{icon}</Link>
            ))}
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-6 py-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-white mb-1">My Career Data</h1>
          <p className="text-surface-400 text-sm mb-8">Manage all your career information in one place</p>

          {/* Tabs */}
          <div className="flex gap-1 mb-6 overflow-x-auto scrollbar-hide pb-1">
            {TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-200 ${activeTab === tab
                    ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
                    : 'text-surface-400 hover:text-white hover:bg-white/[0.04]'
                  }`}
              >
                <span>{TAB_ICONS[tab]}</span>
                {tab}
              </button>
            ))}
          </div>

          <div className="glass-card p-6">
            <TabContent />
          </div>
        </div>
      </main>
    </div>
  );
}
