'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { login as apiLogin, ApiError } from '@/lib/api';

interface AuthState {
  token: string | null;
  username: string | null;
  loading: boolean;
  error: string | null;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

const SESSION_KEY = 'mha-intel-token';
const SESSION_USER_KEY = 'mha-intel-user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Restore a session on reload — tokens expire server-side (see
  // ACCESS_TOKEN_EXPIRE_MINUTES in the backend), so a stale token here just
  // results in 401s that bubble up as normal API errors.
  useEffect(() => {
    const savedToken = sessionStorage.getItem(SESSION_KEY);
    const savedUser = sessionStorage.getItem(SESSION_USER_KEY);
    if (savedToken) setToken(savedToken);
    if (savedUser) setUsername(savedUser);
  }, []);

  const signIn = async (user: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiLogin(user, password);
      setToken(res.access_token);
      setUsername(user);
      sessionStorage.setItem(SESSION_KEY, res.access_token);
      sessionStorage.setItem(SESSION_USER_KEY, user);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.status === 401
            ? 'Incorrect username or password.'
            : err.message
          : 'Could not reach the backend API. Is it running on the expected port?';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const signOut = () => {
    setToken(null);
    setUsername(null);
    sessionStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(SESSION_USER_KEY);
  };

  return (
    <AuthContext.Provider value={{ token, username, loading, error, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
