import { User, TokenResponse } from './types';

const TOKEN_KEY = 'sen_trafic_token';
const USER_KEY = 'sen_trafic_user';

let tokenCache: string | null = null;
const isClient = typeof window !== 'undefined';

export const getToken = (): string | null => {
  if (!isClient) return null;
  if (tokenCache) return tokenCache;
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) tokenCache = token;
    return token;
  } catch {
    return null;
  }
};

export const setToken = (token: string): void => {
  if (!isClient) return;
  try {
    tokenCache = token;
    localStorage.setItem(TOKEN_KEY, token);
  } catch {}
};

export const removeToken = (): void => {
  if (!isClient) return;
  try {
    tokenCache = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch {}
};

export const isAuthenticated = (): boolean => {
  const token = getToken();
  return !!token && isValidToken(token);
};

export const getUserFromToken = (): User | null => {
  const token = getToken();
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = JSON.parse(atob(parts[1]));
    return {
      id: payload.sub || '',
      email: payload.email || '',
      full_name: payload.full_name || payload.email || '',
      role: payload.role || 'viewer',
      is_active: payload.is_active ?? true,
      created_at: payload.created_at || new Date(0).toISOString(),
    };
  } catch {
    return null;
  }
};

const isValidToken = (token: string): boolean => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return false;
    const decoded = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    return decoded.exp ? decoded.exp > now : true;
  } catch {
    return false;
  }
};

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${apiUrl}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Echec de connexion' }));
    throw new Error(error.detail || 'Echec de connexion');
  }

  // Backend returns { access_token, token_type }
  const data: TokenResponse = await response.json();
  setToken(data.access_token);
  return data;
};

export const logout = (): void => {
  removeToken();
};
