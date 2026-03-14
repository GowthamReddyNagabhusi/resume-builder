import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '@/lib/context/AuthContext';

export default function Signup() {
  const router = useRouter();
  const { register } = useAuth();
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) {
      setError('Passwords do not match');
      return;
    }
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await register(form.email, form.password, form.name);
      router.push('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { label: 'Full Name', name: 'name', type: 'text', placeholder: 'Jane Doe' },
    { label: 'Email', name: 'email', type: 'email', placeholder: 'jane@example.com' },
    { label: 'Password', name: 'password', type: 'password', placeholder: 'Min. 8 characters' },
    { label: 'Confirm Password', name: 'confirm', type: 'password', placeholder: 'Repeat password' },
  ];

  return (
    <div className="min-h-screen bg-surface-950 flex items-center justify-center px-4 relative overflow-hidden">
      <div className="glow-orb w-[500px] h-[500px] bg-purple-600 top-[-100px] left-[-100px]" />
      <div className="glow-orb w-[400px] h-[400px] bg-brand-600 bottom-[-50px] right-[-100px]" />

      <div className="w-full max-w-md relative z-10 animate-scale-in">
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-accent-gradient flex items-center justify-center text-white font-bold shadow-glow">
            CF
          </div>
          <span className="text-xl font-bold text-white">CareerForge</span>
        </div>

        <div className="glass-card p-8">
          <h1 className="text-2xl font-bold text-white text-center mb-2">Create Account</h1>
          <p className="text-sm text-surface-400 text-center mb-8">
            Start building production-quality resumes with AI
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400 animate-slide-down">
                {error}
              </div>
            )}

            {fields.map(({ label, name, type, placeholder }) => (
              <div key={name}>
                <label className="block text-sm font-medium text-surface-300 mb-1.5">{label}</label>
                <input
                  name={name}
                  type={type}
                  required
                  placeholder={placeholder}
                  value={form[name]}
                  onChange={handleChange}
                  className="input-premium"
                />
              </div>
            ))}

            <button type="submit" disabled={loading} className="btn-primary w-full text-center !mt-6">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="spinner !w-4 !h-4 !border-2" />
                  Creating account…
                </span>
              ) : 'Create Account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-surface-500">
            Already have an account?{' '}
            <Link href="/auth/login" className="text-brand-400 hover:text-brand-300 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
