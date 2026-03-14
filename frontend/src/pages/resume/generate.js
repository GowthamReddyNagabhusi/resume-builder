import React, { useState, useEffect } from 'react';
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

export default function ResumeGenerate() {
  const router = useRouter();
  const { user, loading: authLoading, logout } = useAuth();
  const [jobDescription, setJobDescription] = useState('');
  const [jobRole, setJobRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (!authLoading && !user) router.replace('/auth/login');
  }, [user, authLoading, router]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!jobDescription.trim()) {
      setError('Please paste a job description');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess(null);

    try {
      const response = await apiClient.generateResume(jobDescription, null, jobRole);
      setSuccess(response);
    } catch (err) {
      setError(err.message || 'Generation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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
            <Link key={href} href={href} className={href === '/resume/generate' ? 'nav-link-active flex items-center gap-3' : 'nav-link flex items-center gap-3'}>
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
        </div>

        <div className="max-w-3xl mx-auto px-6 py-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-white mb-1">Generate Resume</h1>
          <p className="text-surface-400 text-sm mb-8">Paste a job description and AI will compile a tailored resume from your career data</p>

          {success ? (
            <div className="glass-card p-8 text-center animate-scale-in">
              <div className="text-5xl mb-4">🎉</div>
              <h2 className="text-2xl font-bold text-white mb-2">Resume Generated!</h2>
              <p className="text-surface-400 mb-6">Your AI-compiled resume is ready to download</p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                <a href={apiClient.getResumeDownloadUrl(success.resume_id)} className="btn-primary">
                  📥 Download DOCX
                </a>
                <button onClick={() => { setSuccess(null); setJobDescription(''); setJobRole(''); }} className="btn-secondary">
                  Generate Another
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleGenerate} className="space-y-6">
              {error && (
                <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400 animate-slide-down">
                  {error}
                </div>
              )}

              <div className="glass-card p-6">
                <div className="mb-5">
                  <label className="block text-sm font-medium text-surface-300 mb-2">Target Role (optional)</label>
                  <input
                    type="text"
                    className="input-premium"
                    placeholder="e.g., Senior Software Engineer"
                    value={jobRole}
                    onChange={(e) => setJobRole(e.target.value)}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-surface-300 mb-2">Job Description</label>
                  <textarea
                    required
                    rows={12}
                    className="textarea-premium"
                    placeholder="Paste the full job description here. The AI will analyze requirements and compile a tailored resume from your career data..."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                  />
                  <p className="text-xs text-surface-500 mt-2">
                    {jobDescription.length > 0 ? `${jobDescription.length} characters` : 'Tip: Include the full JD for best results'}
                  </p>
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full text-center py-4 text-base">
                {loading ? (
                  <span className="flex items-center justify-center gap-3">
                    <span className="spinner !w-5 !h-5 !border-2" />
                    AI is compiling your resume…
                  </span>
                ) : '✨ Generate Resume'}
              </button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
