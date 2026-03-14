import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/lib/context/AuthContext';
import { apiClient } from '@/lib/api/client';

export default function ResumesPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [resumes, setResumes] = useState([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!loading && !user) router.replace('/auth/login');
  }, [user, loading, router]);

  useEffect(() => {
    if (!user) return;
    apiClient.getResumes()
      .then(setResumes)
      .catch(() => {})
      .finally(() => setFetching(false));
  }, [user]);

  const handleDelete = async (id) => {
    if (!confirm('Delete this resume?')) return;
    await apiClient.deleteResume(id).catch(() => {});
    setResumes((prev) => prev.filter((r) => r.id !== id));
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><p className="text-gray-500">Loading…</p></div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-bold text-blue-600">ResumeBuilder.AI</Link>
          <div className="flex items-center gap-4 text-sm">
            <Link href="/dashboard" className="text-gray-600 hover:text-blue-600">← Dashboard</Link>
            <Link href="/resume/generate" className="px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              + Generate New
            </Link>
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">My Resumes</h1>

        {fetching ? (
          <p className="text-gray-400">Loading resumes…</p>
        ) : resumes.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center text-gray-400">
            <p className="text-5xl mb-4">📄</p>
            <p className="text-lg mb-4">You haven&apos;t generated any resumes yet.</p>
            <Link href="/resume/generate" className="inline-block px-5 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              Generate your first resume
            </Link>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['Title', 'Template', 'Created', 'Actions'].map((h) => (
                    <th key={h} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {resumes.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{r.title || 'Untitled'}</p>
                      {r.job_title && <p className="text-xs text-gray-400">{r.job_title}</p>}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{r.template_id || '—'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {r.created_at ? new Date(r.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <a
                          href={apiClient.getResumeDownloadUrl(r.id, 'docx')}
                          className="text-sm text-blue-600 hover:underline"
                        >
                          DOCX
                        </a>
                        <a
                          href={apiClient.getResumeDownloadUrl(r.id, 'txt')}
                          className="text-sm text-blue-600 hover:underline"
                        >
                          TXT
                        </a>
                        <button
                          onClick={() => handleDelete(r.id)}
                          className="text-sm text-red-500 hover:text-red-700"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
