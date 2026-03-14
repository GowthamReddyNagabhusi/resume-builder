import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/lib/context/AuthContext';
import { apiClient } from '@/lib/api/client';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/career', label: 'Career Data', icon: '📝' },
  { href: '/resume/generate', label: 'Generate', icon: '✨' },
  { href: '/resume', label: 'My Resumes', icon: '📄' },
];

const PLATFORM_ICONS = {
  github: '🐙', linkedin: '💼', leetcode: '🧩', codeforces: '⚔️',
  hackerrank: '💚', codechef: '👨‍🍳', portfolio: '🌐', twitter: '🐦',
  kaggle: '📊', other: '🔗',
};

export default function Dashboard() {
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const [summary, setSummary] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [platforms, setPlatforms] = useState([]);

  useEffect(() => {
    if (!loading && !user) router.replace('/auth/login');
  }, [user, loading, router]);

  useEffect(() => {
    if (!user) return;
    apiClient.getCareerSummary().then(setSummary).catch(() => { });
    apiClient.getResumes().then((data) => {
      setResumes(data?.resumes || data || []);
    }).catch(() => { });
    apiClient.getPlatforms().then(setPlatforms).catch(() => { });
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <div className="spinner spinner-lg" />
      </div>
    );
  }

  const stats = [
    { label: 'Education', value: summary?.education_count ?? '–', icon: '🎓', color: 'from-blue-500/20 to-cyan-500/20' },
    { label: 'Experience', value: summary?.experience_count ?? '–', icon: '💼', color: 'from-purple-500/20 to-pink-500/20' },
    { label: 'Skills', value: summary?.skills_count ?? '–', icon: '⚡', color: 'from-amber-500/20 to-orange-500/20' },
    { label: 'Achievements', value: summary?.achievements_count ?? '–', icon: '🏅', color: 'from-rose-500/20 to-red-500/20' },
    { label: 'Resumes', value: Array.isArray(resumes) ? resumes.length : 0, icon: '📄', color: 'from-emerald-500/20 to-teal-500/20' },
    { label: 'Platforms', value: summary?.platforms_count ?? '–', icon: '🔗', color: 'from-indigo-500/20 to-violet-500/20' },
  ];

  const quickActions = [
    { href: '/career', icon: '📝', title: 'Manage Career Data', desc: 'Add education, experience, skills, projects', color: 'from-brand-500/10 to-purple-500/10' },
    { href: '/resume/generate', icon: '✨', title: 'Generate Resume', desc: 'Paste a job description and get a tailored resume', color: 'from-emerald-500/10 to-teal-500/10' },
    { href: '/resume', icon: '📄', title: 'View Resumes', desc: 'Browse and download generated resumes', color: 'from-amber-500/10 to-orange-500/10' },
  ];

  return (
    <div className="min-h-screen bg-surface-950 flex">
      {/* Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 border-r border-white/[0.06] p-4">
        <div className="flex items-center gap-2 px-3 mb-8">
          <div className="w-8 h-8 rounded-lg bg-accent-gradient flex items-center justify-center text-white font-bold text-sm shadow-glow">
            CF
          </div>
          <span className="text-lg font-bold text-white">CareerForge</span>
        </div>

        <nav className="flex-1 space-y-1">
          {NAV_ITEMS.map(({ href, label, icon }) => (
            <Link
              key={href}
              href={href}
              className={href === '/dashboard' ? 'nav-link-active flex items-center gap-3' : 'nav-link flex items-center gap-3'}
            >
              <span>{icon}</span>
              {label}
            </Link>
          ))}
        </nav>

        <button
          onClick={() => { logout(); router.push('/'); }}
          className="btn-ghost text-sm text-surface-500 w-full text-left flex items-center gap-3"
        >
          <span>🚪</span>
          Sign Out
        </button>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        {/* Mobile nav */}
        <div className="lg:hidden border-b border-white/[0.06] p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-accent-gradient flex items-center justify-center text-white font-bold text-xs">CF</div>
            <span className="font-bold text-white">CareerForge</span>
          </div>
          <div className="flex items-center gap-2">
            {NAV_ITEMS.slice(1).map(({ href, icon }) => (
              <Link key={href} href={href} className="btn-ghost !px-2">{icon}</Link>
            ))}
            <button onClick={() => { logout(); router.push('/'); }} className="btn-ghost !px-2">🚪</button>
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-6 py-8 animate-fade-in">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-1">
              Welcome back{user?.name ? `, ${user.name}` : ''}
            </h1>
            <p className="text-surface-400">Here&apos;s your career data overview</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {stats.map(({ label, value, icon, color }) => (
              <div key={label} className="stat-card group">
                <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl`} />
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-surface-400">{label}</span>
                    <span className="text-xl">{icon}</span>
                  </div>
                  <p className="text-3xl font-bold text-white">{value}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quick Actions */}
            <div>
              <h2 className="section-heading mb-4">Quick Actions</h2>
              <div className="space-y-3">
                {quickActions.map(({ href, icon, title, desc, color }) => (
                  <Link key={href} href={href} className="glass-card-hover p-5 flex items-center gap-4 block">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center text-xl shrink-0`}>
                      {icon}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{title}</p>
                      <p className="text-xs text-surface-400 mt-0.5">{desc}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              {/* Connected Platforms */}
              {platforms.length > 0 && (
                <div>
                  <h2 className="section-heading mb-4">Connected Platforms</h2>
                  <div className="glass-card p-5">
                    <div className="flex flex-wrap gap-3">
                      {platforms.map((p) => (
                        <a
                          key={p.id}
                          href={p.profile_url || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-surface-800/60 hover:bg-surface-700/60 transition-colors border border-white/[0.06] hover:border-white/[0.12]"
                          title={`${p.platform}${p.username ? ': ' + p.username : ''}`}
                        >
                          <span className="text-lg">{PLATFORM_ICONS[p.platform] || '🔗'}</span>
                          <span className="text-sm text-white capitalize">{p.platform}</span>
                          {p.username && <span className="text-xs text-surface-400">@{p.username}</span>}
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Recent Resumes */}
              <div>
                <h2 className="section-heading mb-4">Recent Resumes</h2>
                <div className="glass-card p-5">
                  {!Array.isArray(resumes) || resumes.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-4xl mb-3">📋</p>
                      <p className="text-surface-400 text-sm mb-4">No resumes generated yet</p>
                      <Link href="/resume/generate" className="btn-primary text-sm !py-2 !px-4">
                        Generate First Resume
                      </Link>
                    </div>
                  ) : (
                    <ul className="divide-y divide-white/[0.06]">
                      {resumes.slice(0, 5).map((r) => (
                        <li key={r.id} className="py-3 flex justify-between items-center">
                          <div>
                            <p className="font-medium text-sm text-white">{r.title || 'Untitled Resume'}</p>
                            <p className="text-xs text-surface-500 mt-0.5">
                              {r.generated_at || r.created_at ? new Date(r.generated_at || r.created_at).toLocaleDateString() : ''}
                            </p>
                          </div>
                          <a href={apiClient.getResumeDownloadUrl(r.id)} className="badge text-xs">
                            Download
                          </a>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
