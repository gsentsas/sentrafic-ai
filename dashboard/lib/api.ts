import { getToken } from './auth';
import {
  DashboardOverview,
  Site,
  Camera,
  Alert,
  ClassDistribution,
  TrafficAggregate,
  CameraTrafficData,
  LiveSummaryResponse,
  User,
  UserCreate,
  UserUpdate,
  UserPasswordChange,
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

/**
 * Generic fetch wrapper with auth and error handling.
 * FastAPI backend returns data directly (no wrapper object).
 */
export const apiFetch = async <T>(
  path: string,
  options: FetchOptions = {}
): Promise<T> => {
  const url = `${BASE_URL}${path}`;
  const token = getToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      throw new Error('Unauthorized');
    }

    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || error.message || `API Error: ${response.status}`);
  }

  return response.json();
};

// ──────────────────────────────────────────────
// Dashboard
// ──────────────────────────────────────────────
export const getOverview = async (): Promise<DashboardOverview> => {
  return apiFetch<DashboardOverview>('/api/dashboard/overview');
};

export const getLiveSummary = async (
  filters?: { siteId?: string; status?: 'online' | 'offline' | 'error' | '' }
): Promise<LiveSummaryResponse> => {
  const query = new URLSearchParams();
  if (filters?.siteId) query.append('site_id', filters.siteId);
  if (filters?.status) query.append('status', filters.status);
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return apiFetch<LiveSummaryResponse>(`/api/dashboard/live-summary${suffix}`);
};

// ──────────────────────────────────────────────
// Sites
// ──────────────────────────────────────────────
export const getSites = async (skip = 0, limit = 100): Promise<Site[]> => {
  return apiFetch<Site[]>(`/api/sites?skip=${skip}&limit=${limit}`);
};

export const getSiteById = async (siteId: string): Promise<Site> => {
  return apiFetch<Site>(`/api/sites/${siteId}`);
};

export const createSite = async (siteData: Partial<Site>): Promise<Site> => {
  return apiFetch<Site>('/api/sites', {
    method: 'POST',
    body: JSON.stringify(siteData),
  });
};

export const updateSite = async (siteId: string, siteData: Partial<Site>): Promise<Site> => {
  return apiFetch<Site>(`/api/sites/${siteId}`, {
    method: 'PUT',
    body: JSON.stringify(siteData),
  });
};

// ──────────────────────────────────────────────
// Cameras
// ──────────────────────────────────────────────
export const getCameras = async (
  siteId?: string,
  skip = 0,
  limit = 100
): Promise<Camera[]> => {
  const query = new URLSearchParams({ skip: String(skip), limit: String(limit) });
  if (siteId) query.append('site_id', siteId);
  return apiFetch<Camera[]>(`/api/cameras?${query}`);
};

export const getCameraById = async (cameraId: string): Promise<Camera> => {
  return apiFetch<Camera>(`/api/cameras/${cameraId}`);
};

export const createCamera = async (cameraData: Partial<Camera>): Promise<Camera> => {
  return apiFetch<Camera>('/api/cameras', {
    method: 'POST',
    body: JSON.stringify(cameraData),
  });
};

export const updateCamera = async (cameraId: string, cameraData: Partial<Camera>): Promise<Camera> => {
  return apiFetch<Camera>(`/api/cameras/${cameraId}`, {
    method: 'PUT',
    body: JSON.stringify(cameraData),
  });
};

export const getCameraTraffic = async (
  cameraId: string,
  hours = 24
): Promise<CameraTrafficData> => {
  return apiFetch<CameraTrafficData>(`/api/cameras/${cameraId}/traffic?hours=${hours}`);
};

// ──────────────────────────────────────────────
// Alerts
// ──────────────────────────────────────────────
export const getAlerts = async (
  skip = 0,
  limit = 100,
  severity?: string,
  isResolved?: boolean
): Promise<Alert[]> => {
  const query = new URLSearchParams({ skip: String(skip), limit: String(limit) });
  if (severity) query.append('severity', severity);
  if (isResolved !== undefined) query.append('is_resolved', String(isResolved));
  return apiFetch<Alert[]>(`/api/alerts?${query}`);
};

export const getAlertById = async (alertId: string): Promise<Alert> => {
  return apiFetch<Alert>(`/api/alerts/${alertId}`);
};

export const resolveAlert = async (alertId: string): Promise<Alert> => {
  return apiFetch<Alert>(`/api/alerts/${alertId}/resolve`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
};

// ──────────────────────────────────────────────
// Analytics
// ──────────────────────────────────────────────
export const getTrafficAnalytics = async (
  startDate: string,
  endDate: string,
  cameraId?: string,
  granularity: 'hour' | 'day' = 'hour'
): Promise<TrafficAggregate[]> => {
  const query = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
    granularity,
  });
  if (cameraId) query.append('camera_id', cameraId);
  return apiFetch<TrafficAggregate[]>(`/api/analytics/traffic?${query}`);
};

export const getClassDistribution = async (
  startDate: string,
  endDate: string,
  cameraId?: string
): Promise<ClassDistribution[]> => {
  // Backend distribution endpoint uses period_hours — compute from date range
  const start = new Date(startDate).getTime();
  const end = new Date(endDate).getTime();
  const periodHours = Math.max(1, Math.round((end - start) / (1000 * 60 * 60)));
  const query = new URLSearchParams({ period_hours: String(periodHours) });
  if (cameraId) query.append('camera_id', cameraId);
  // Backend returns a single object, wrap in array for consistency
  const result = await apiFetch<ClassDistribution>(`/api/analytics/distribution?${query}`);
  return [result];
};

export const exportTrafficCsv = async (
  startDate: string,
  endDate: string,
  cameraId?: string,
  siteId?: string
): Promise<Blob> => {
  const query = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
  });
  if (cameraId) query.append('camera_id', cameraId);
  if (siteId) query.append('site_id', siteId);

  const response = await fetch(`${BASE_URL}/api/exports/traffic.csv?${query}`, {
    headers: {
      Authorization: `Bearer ${getToken() || ''}`,
    },
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Échec de l\'export CSV');
  }

  return response.blob();
};

/** Déclenche le téléchargement d'un Blob dans le navigateur. */
export const downloadBlob = (blob: Blob, filename: string): void => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// ──────────────────────────────────────────────
// Auth
// ──────────────────────────────────────────────
export const loginApi = async (email: string, password: string) => {
  return apiFetch<{ access_token: string; token_type: string }>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
};

// ──────────────────────────────────────────────
// Users
// ──────────────────────────────────────────────
export const getMe = async (): Promise<User> =>
  apiFetch<User>('/api/users/me');

export const getUsers = async (): Promise<User[]> =>
  apiFetch<User[]>('/api/users');

export const createUser = async (data: UserCreate): Promise<User> =>
  apiFetch<User>('/api/users', { method: 'POST', body: JSON.stringify(data) });

export const updateUser = async (userId: string, data: UserUpdate): Promise<User> =>
  apiFetch<User>(`/api/users/${userId}`, { method: 'PUT', body: JSON.stringify(data) });

export const changeMyPassword = async (data: UserPasswordChange): Promise<{ message: string }> =>
  apiFetch<{ message: string }>('/api/users/me/password', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
