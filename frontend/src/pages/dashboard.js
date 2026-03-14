import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/lib/context/AuthContext';
import { apiClient } from '@/lib/api/client';

export default function Dashboard() {
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const [summary, setSummary] = useState(null);
  const [resumes, setResumes] = useState([]);

  useEffect(() => {
    if (!loading && !user) {
      router.replace('/auth/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (!user) return;
    apiClient.getCareerSummary().then(setSummary).catch(() => {});
    apiClient.getResumes().then(setResumes).catch(() => {});
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading…</p>
      </div>
    );
  }

  const stats = [
    { label: 'Education', value: summary?.education_count ?? '–' },
    { label: 'Experience', value: summary?.experience_count ?? '–' },
    { label: 'Skills', value: summary?.skills_count ?? '–' },
    { label: 'Resumes', value: resumes.length },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <nav className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <span className="text-xl font-bold text-blue-600">ResumeBuilder.AI</span>
          <div className="flex items-center gap-6 text-sm">
            <Link href="/career" className="text-gray-600 hover:text-blue-600">Career Data</Link>
            <Link href="/resume/generate" className="text-gray-600 hover:text-blue-600">Generate</Link>
            <Link href="/resume" className="text-gray-600 hover:text-blue-600">My Resumes</Link>
            <button
              onClick={() => { logout(); router.push('/'); }}
              className="text-gray-600 hover:text-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Welcome back{user?.name ? `, ${user.name}` : ''}!
        </h1>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          {stats.map(({ label, value }) => (
            <div key={label} className="bg-white p-6 rounded-lg shadow text-center">
              <p className="text-sm text-gray-500">{label}</p>
              <p className="text-4xl font-bold text-blue-600 mt-1">{value}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                href="/career"
                className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition"
              >
                <span className="text-2xl">📝</span>
                <div>
                  <p className="font-medium">Manage Career Data</p>
                  <p className="text-xs text-gray-500">Add education, experience, skills, projects</p>
                </div>
              </Link>
              <Link
                href="/resume/generate"
                className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition"
              >
                <span className="text-2xl">✨</span>
                <div>
                  <p className="font-medium">Generate a Resume</p>
                  <p className="text-xs text-gray-500">Paste a job description and get a tailored resume</p>
                </div>
              </Link>
              <Link
                href="/resume"
                className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition"
              >
                <span className="text-2xl">📄</span>
                <div>
                  <p className="font-medium">View My Resumes</p>
                  <p className="text-xs text-gray-500">Browse and download generated resumes</p>
                </div>
              </Link>
            </div>
          </div>

          {/* Recent Resumes */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Resumes</h2>
            {resumes.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-4xl mb-2">📋</p>
                <p>No resumes generated yet.</p>
                <Link href="/resume/generate" className="mt-3 inline-block text-sm text-blue-600 hover:underline">
                  Generate your first resume →
                </Link>
              </div>
            ) : (
              <ul className="divide-y divide-gray-100">
                {resumes.slice(0, 5).map((r) => (
                  <li key={r.id} className="py-3 flex justify-between items-center">
                    <div>
                      <p className="font-medium text-sm">{r.title || 'Untitled Resume'}</p>
                      <p className="text-xs text-gray-400">
                        {r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}
                      </p>
                    </div>
                    <a
                      href={apiClient.getResumeDownloadUrl(r.id)}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Download
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

