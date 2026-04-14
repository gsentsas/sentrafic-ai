// ─── Backend uses snake_case — these match the actual JSON responses ───

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string;
  role?: string;
}

export interface UserUpdate {
  full_name?: string;
  role?: string;
  is_active?: boolean;
}

export interface UserPasswordChange {
  current_password: string;
  new_password: string;
}

export interface Site {
  id: string;
  name: string;
  slug: string;
  address: string;
  city: string;
  latitude: number;
  longitude: number;
  site_type: string;
  is_active: boolean;
  camera_count: number;
  created_at: string;
}

export interface Camera {
  id: string;
  site_id: string;
  site_name: string | null;
  name: string;
  stream_url: string;
  status: 'online' | 'offline' | 'error';
  location_description: string;
  is_active: boolean;
  last_seen_at: string | null;
  health_label: 'healthy' | 'delayed' | 'offline' | 'unknown';
  created_at: string;
}

export interface TrafficAggregate {
  id: string;
  camera_id: string;
  timestamp: string;
  period_seconds: number;
  car_count: number;
  bus_count: number;
  truck_count: number;
  motorcycle_count: number;
  person_count: number;
  total_count: number;
  avg_occupancy: number;
  congestion_level: 'free' | 'moderate' | 'heavy' | 'blocked';
}

export interface Alert {
  id: string;
  camera_id: string;
  site_id: string;
  site_name: string | null;
  camera_name: string | null;
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  short_description: string;
  recommended_action: string;
  is_resolved: boolean;
  resolved_at: string | null;
  created_at: string;
}

export interface TrafficTrendPoint {
  timestamp: string;
  count: number;
}

export interface ClassDistribution {
  distribution: Record<string, number>;
  total_count: number;
  period_hours: number;
}

export interface WatchlistItem {
  camera_id: string;
  camera_name: string;
  status: string;
  last_seen_at: string | null;
}

export interface DashboardOverview {
  summary: {
    total_sites: number;
    total_cameras: number;
    cameras_online: number;
    cameras_offline: number;
    online_percentage: number;
    total_vehicles_today: number;
    alerts_unresolved: number;
    alerts_critical: number;
  };
  congestion: {
    avg_level: string;
    total_vehicles_1h: number;
    by_class: Record<string, number>;
  };
  recent_alerts: Alert[];
  traffic_trend_24h: TrafficTrendPoint[];
  watchlist: WatchlistItem[];
  timestamp: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface CameraTrafficData {
  camera_id: string;
  camera_name: string;
  status: string;
  last_seen_at: string | null;
  trend: Array<{ timestamp: string; count: number }>;
  summary: {
    total_vehicles: number;
    avg_congestion_level: string;
    by_class: Record<string, number>;
  };
  distribution: {
    distribution: Record<string, number>;
    total_count: number;
  };
  recent_alerts: Array<{
    id: string;
    alert_type: string;
    severity: string;
    message: string;
    is_resolved: boolean;
    created_at: string | null;
  }>;
  last_reading: {
    total_count: number;
    congestion_level: string;
    avg_occupancy: number;
    timestamp: string | null;
    is_stale?: boolean;
  } | null;
}

export interface LiveSummaryCamera {
  camera_id: string;
  camera_name: string;
  site_name: string | null;
  status: 'online' | 'offline' | 'error';
  stream_url: string;
  last_seen_at: string | null;
  last_reading: {
    total_count: number;
    congestion_level: string;
    avg_occupancy: number;
    timestamp: string | null;
    is_stale?: boolean;
  } | null;
}

export interface LiveSummaryResponse {
  cameras: LiveSummaryCamera[];
  timestamp: string;
}
