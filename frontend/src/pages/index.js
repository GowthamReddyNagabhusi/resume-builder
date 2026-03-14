import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between items-center">
            <div className="text-2xl font-bold text-blue-600">ResumeBuilder.AI</div>
            <div className="flex gap-4">
              <a href="/auth/login" className="text-gray-600 hover:text-blue-600">Login</a>
              <a href="/auth/signup" className="bg-blue-600 text-white px-4 py-2 rounded">Sign Up</a>
            </div>
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            AI-Powered Resume Compiler
          </h1>
          <p className="text-2xl text-gray-600 mb-8">
            Compile structured career data into role-specific resumes using AI
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
            <div className="bg-white p-8 rounded-lg shadow">
              <h3 className="text-xl font-bold mb-4">1. Career Data</h3>
              <p>Enter education, experience, skills, and projects once</p>
            </div>
            <div className="bg-white p-8 rounded-lg shadow">
              <h3 className="text-xl font-bold mb-4">2. AI Analysis</h3>
              <p>AI analyzes job descriptions and ranks relevant content</p>
            </div>
            <div className="bg-white p-8 rounded-lg shadow">
              <h3 className="text-xl font-bold mb-4">3. Resume Generation</h3>
              <p>Generate optimized, role-specific resumes instantly</p>
            </div>
          </div>

          <a href="/auth/signup" className="inline-block mt-12 bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-bold hover:bg-blue-700">
            Get Started
          </a>
        </div>
      </main>
    </div>
  );
}
