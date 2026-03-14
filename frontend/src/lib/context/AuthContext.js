import { createContext, useState, useEffect, useCallback, useContext } from 'react';
import { apiClient } from '@/lib/api/client';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore session on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    apiClient.setToken(token);
    apiClient
      .getCurrentUser()
      .then((u) => setUser(u))
      .catch(() => {
        // Token is expired or invalid – clean up
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        apiClient.setToken(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await apiClient.login(email, password);
    localStorage.setItem('access_token', data.access_token);
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }
    apiClient.setToken(data.access_token);
    const me = await apiClient.getCurrentUser();
    setUser(me);
    return me;
  }, []);

  const register = useCallback(async (email, password, name) => {
    await apiClient.register(email, password, name);
    return login(email, password);
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    apiClient.setToken(null);
    setUser(null);
  }, []);

  const refreshToken = useCallback(async () => {
    const token = localStorage.getItem('refresh_token');
    if (!token) return false;
    try {
      const data = await apiClient.refreshToken(token);
      localStorage.setItem('access_token', data.access_token);
      apiClient.setToken(data.access_token);
      return true;
    } catch {
      logout();
      return false;
    }
  }, [logout]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
