'use client';

import { useState } from 'react';
import { Radio, Lock, User, Loader2, AlertTriangle } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function LoginScreen() {
  const { signIn, loading, error } = useAuth();
  const [username, setUsername] = useState('insp.sharma');
  const [password, setPassword] = useState('changeme123');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signIn(username, password);
    } catch {
      // error is surfaced via useAuth().error — nothing else to do here
    }
  };

  return (
    <main className="h-full flex items-center justify-center bg-base-900">
      <div className="w-full max-w-sm rounded-lg border border-base-600 bg-base-800 p-6 shadow-panel">
        <div className="flex items-center gap-2 mb-6">
          <div className="relative h-8 w-8 rounded-sm bg-base-900 border border-signal/30 flex items-center justify-center">
            <Radio size={16} className="text-signal" />
          </div>
          <div>
            <p className="font-display font-semibold text-sm text-ink-100 tracking-label uppercase">
              MHA Intel Suite
            </p>
            <p className="text-[10px] text-ink-500 font-mono tracking-label">SIH-26189 · SIGN IN</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <label className="block">
            <span className="text-[11px] text-ink-500 font-mono tracking-label uppercase">Username</span>
            <div className="mt-1 flex items-center gap-2 rounded-md border border-base-600 bg-base-900 px-3 py-2 focus-within:border-signal/60">
              <User size={14} className="text-ink-500" />
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="flex-1 bg-transparent text-sm text-ink-100 outline-none font-body"
                autoComplete="username"
              />
            </div>
          </label>

          <label className="block">
            <span className="text-[11px] text-ink-500 font-mono tracking-label uppercase">Password</span>
            <div className="mt-1 flex items-center gap-2 rounded-md border border-base-600 bg-base-900 px-3 py-2 focus-within:border-signal/60">
              <Lock size={14} className="text-ink-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="flex-1 bg-transparent text-sm text-ink-100 outline-none font-body"
                autoComplete="current-password"
              />
            </div>
          </label>

          {error && (
            <p className="flex items-start gap-1.5 text-[12px] text-threat-kingpin">
              <AlertTriangle size={13} className="mt-0.5 shrink-0" />
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 rounded-md bg-signal text-base-950 py-2.5 text-[13px] font-medium hover:bg-signal/90 transition-colors disabled:opacity-60"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="mt-4 text-[10px] text-ink-700 font-mono">
          Demo credentials pre-filled: insp.sharma / changeme123 (investigator). Backend must be
          running at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}.
        </p>
      </div>
    </main>
  );
}
