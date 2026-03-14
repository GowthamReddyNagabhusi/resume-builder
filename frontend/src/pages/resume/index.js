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

export default function ResumesPage() {
  const router = useRouter();
  const { user, loading: authLoading, logout } = useAuth();
  const [resumes, setResumes] = useState([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) router.replace('/auth/login');
  }, [user, authLoading, router]);

  useEffect(() => {
    if (!user) return;
    apiClient.getResumes()
      .then((data) => setResumes(data?.resumes || data || []))
      .catch(() => { })
      .finally(() => setFetching(false));
  }, [user]);

  if (authLoading) {
    return <div className="min-h-screen bg-surface-950 flex items-center justify-center"><div className="spinner spinner-lg" /></div>;
  }

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
            <Link key={href} href={href} className={href === '/resume' ? 'nav-link-active flex items-center gap-3' : 'nav-link flex items-center gap-3'}>
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
          <Link href="/resume/generate" className="btn-primary text-sm !py-2 !px-4">+ Generate</Link>
        </div>

        <div className="max-w-5xl mx-auto px-6 py-8 animate-fade-in">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">My Resumes</h1>
              <p className="text-surface-400 text-sm">Browse and download your generated resumes</p>
            </div>
            <Link href="/resume/generate" className="btn-primary hidden sm:inline-flex text-sm">
              ✨ Generate New
            </Link>
          </div>

          {fetching ? (
            <div className="flex justify-center py-12"><div className="spinner spinner-lg" /></div>
          ) : !Array.isArray(resumes) || resumes.length === 0 ? (
            <div className="glass-card p-16 text-center">
              <div className="text-6xl mb-4">📄</div>
              <h2 className="text-xl font-bold text-white mb-2">No resumes yet</h2>
              <p className="text-surface-400 mb-6 max-w-sm mx-auto">
                Generate your first AI-compiled resume by pasting a job description
              </p>
              <Link href="/resume/generate" className="btn-primary">
                Generate First Resume
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {resumes.map((r) => (
                <div key={r.id} className="glass-card-hover p-5 flex flex-col">
                  <div className="flex items-start justify-between mb-3">
                    <div className="w-10 h-10 rounded-xl bg-brand-500/10 flex items-center justify-center text-lg shrink-0">
                      📄
                    </div>
                    <span className="text-xs text-surface-500">
                      {r.generated_at || r.created_at ? new Date(r.generated_at || r.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                  <h3 className="font-semibold text-white text-sm mb-1 line-clamp-2">
                    {r.title || 'Untitled Resume'}
                  </h3>
                  {r.job_role && (
                    <p className="text-xs text-surface-400 mb-3">{r.job_role}</p>
                  )}
                  <div className="mt-auto pt-3 border-t border-white/[0.06] flex items-center gap-2">
                    <a href={apiClient.getResumeDownloadUrl(r.id)} className="badge text-xs flex-1 text-center justify-center">
                      📥 Download
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
