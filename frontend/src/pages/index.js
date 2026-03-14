import React from 'react';
import Link from 'next/link';

const FEATURES = [
  {
    icon: '🎯',
    title: 'Career Data Compiler',
    desc: 'Enter your education, experience, skills, and projects once. Your data becomes the single source of truth.',
  },
  {
    icon: '🤖',
    title: 'AI-Powered Analysis',
    desc: 'Groq AI analyzes job descriptions, ranks your most relevant content, and generates ATS-optimized bullets.',
  },
  {
    icon: '📄',
    title: 'Instant Generation',
    desc: 'Generate role-specific, professionally formatted resumes in seconds — DOCX or PDF, ready to submit.',
  },
  {
    icon: '🔗',
    title: 'GitHub Integration',
    desc: 'Connect your GitHub profile to auto-import repositories, languages, and contributions into your resume.',
  },
  {
    icon: '📊',
    title: 'ATS Optimization',
    desc: 'AI scores your resume against job descriptions and suggests keyword improvements to beat tracking systems.',
  },
  {
    icon: '⚡',
    title: 'One-Click Apply',
    desc: 'Track job applications with built-in Kanban board. Generate tailored resumes for each application instantly.',
  },
];

const STEPS = [
  { num: '01', title: 'Add Career Data', desc: 'Enter education, experience, skills, projects, and certifications' },
  { num: '02', title: 'Paste Job Description', desc: 'Paste the target job description and select a template' },
  { num: '03', title: 'AI Compiles Resume', desc: 'AI selects relevant content, generates bullets, optimizes for ATS' },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-surface-950 relative overflow-hidden">
      {/* Background decoration */}
      <div className="glow-orb w-[600px] h-[600px] bg-brand-600 top-[-200px] left-[-200px]" />
      <div className="glow-orb w-[500px] h-[500px] bg-purple-600 top-[200px] right-[-150px]" />
      <div className="glow-orb w-[400px] h-[400px] bg-brand-500 bottom-[-100px] left-[30%]" />

      {/* Nav */}
      <nav className="relative z-10 border-b border-white/[0.06]">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-accent-gradient flex items-center justify-center text-white font-bold text-sm shadow-glow">
                CF
              </div>
              <span className="text-lg font-bold text-white">CareerForge</span>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/auth/login" className="btn-ghost text-sm">
                Sign In
              </Link>
              <Link href="/auth/signup" className="btn-primary !py-2 !px-5 text-sm">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 pt-20 pb-24 px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center animate-fade-in">
          <div className="badge mb-6 mx-auto">✨ AI-Powered Resume Compiler</div>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-[1.1] mb-6">
            Build Resumes That
            <br />
            <span className="gradient-text">Land Interviews</span>
          </h1>
          <p className="text-lg sm:text-xl text-surface-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Enter your career data once. AI compiles role-specific, ATS-optimized resumes
            tailored to every job description — in seconds.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/signup" className="btn-primary text-base px-8 py-4">
              Start Building Free →
            </Link>
            <Link href="/auth/login" className="btn-secondary text-base">
              I Have an Account
            </Link>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative z-10 py-20 px-6 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-3xl font-bold text-white text-center mb-16">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {STEPS.map((step, i) => (
              <div key={step.num} className="glass-card p-8 text-center animate-slide-up" style={{ animationDelay: `${i * 0.15}s` }}>
                <div className="text-4xl font-black gradient-text mb-4">{step.num}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-surface-400 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative z-10 py-20 px-6 lg:px-8 border-t border-white/[0.04]">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-bold text-white text-center mb-4">
            Everything You Need
          </h2>
          <p className="text-surface-400 text-center mb-16 max-w-xl mx-auto">
            From data entry to ATS optimization — a complete toolkit for job seekers.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((feat, i) => (
              <div key={feat.title} className="glass-card-hover p-7 animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="text-3xl mb-4">{feat.icon}</div>
                <h3 className="text-base font-semibold text-white mb-2">{feat.title}</h3>
                <p className="text-sm text-surface-400 leading-relaxed">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 py-24 px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <div className="glass-card p-12 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-brand-600/10 to-purple-600/10" />
            <div className="relative z-10">
              <h2 className="text-3xl font-bold text-white mb-4">
                Ready to Build Better Resumes?
              </h2>
              <p className="text-surface-400 mb-8 max-w-lg mx-auto">
                Join thousands of professionals who compile their career data once
                and generate perfect resumes for every opportunity.
              </p>
              <Link href="/auth/signup" className="btn-primary text-base px-8 py-4">
                Get Started — It&apos;s Free
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/[0.06] py-8 px-6">
        <div className="mx-auto max-w-7xl flex items-center justify-between text-sm text-surface-500">
          <span>© 2026 CareerForge. All rights reserved.</span>
          <span>Built with AI · Open Source</span>
        </div>
      </footer>
    </div>
  );
}
