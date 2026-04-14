import {
  LayoutDashboard,
  MapPin,
  Camera,
  Radio,
  Bell,
  BarChart3,
  Settings,
} from 'lucide-react';

export const APP_NAME = 'SEN TRAFIC AI';
export const REFRESH_INTERVAL = 30000; // 30 seconds

export const NAV_ITEMS = [
  {
    label: 'Tableau de bord',
    href: '/overview',
    icon: LayoutDashboard,
  },
  {
    label: 'Sites',
    href: '/sites',
    icon: MapPin,
  },
  {
    label: 'Cameras',
    href: '/cameras',
    icon: Camera,
  },
  {
    label: 'Supervision live',
    href: '/live',
    icon: Radio,
  },
  {
    label: 'Alertes',
    href: '/alerts',
    icon: Bell,
  },
  {
    label: 'Analytique',
    href: '/analytics',
    icon: BarChart3,
  },
  {
    label: 'Parametres',
    href: '/settings',
    icon: Settings,
  },
];

export const CONGESTION_COLORS: Record<string, string> = {
  free: '#10B981',
  moderate: '#F59E0B',
  heavy: '#EF4444',
  blocked: '#7C3AED',
};

export const CONGESTION_LABELS: Record<string, string> = {
  free: 'Fluide',
  moderate: 'Modere',
  heavy: 'Dense',
  blocked: 'Bloque',
};

export const ALERT_SEVERITY_COLORS: Record<string, string> = {
  info: '#06B6D4',
  warning: '#F59E0B',
  critical: '#EF4444',
};

export const ALERT_SEVERITY_LABELS: Record<string, string> = {
  info: 'Info',
  warning: 'Avertissement',
  critical: 'Critique',
};

export const ALERT_TYPE_LABELS: Record<string, string> = {
  congestion: 'Congestion',
  stopped_vehicle: 'Vehicule arrete',
  camera_offline: 'Camera hors ligne',
  no_recent_data: 'Pas de donnees recentes',
  abnormal_low_traffic: 'Trafic anormalement faible',
  abnormal_high_traffic: 'Trafic anormalement eleve',
  zone_overflow: 'Debordement de zone',
};

export const CAMERA_STATUS_COLORS: Record<string, string> = {
  online: '#10B981',
  offline: '#6B7280',
  error: '#EF4444',
};

export const CAMERA_STATUS_LABELS: Record<string, string> = {
  online: 'En ligne',
  offline: 'Hors ligne',
  error: 'Erreur',
};

export const CAMERA_HEALTH_LABELS: Record<string, string> = {
  healthy: 'Operationnelle',
  delayed: 'Retard',
  offline: 'Hors ligne',
  unknown: 'Inconnu',
};

export const CLASS_LABELS: Record<string, string> = {
  car: 'Voiture',
  bus: 'Bus',
  truck: 'Camion',
  motorcycle: 'Moto',
  person: 'Pieton',
};

export const CLASS_COLORS: Record<string, string> = {
  car: '#2563EB',
  bus: '#10B981',
  truck: '#F59E0B',
  motorcycle: '#A855F7',
  person: '#6B7280',
};

export const VEHICLE_CLASSES = [
  { key: 'car', label: 'Voiture', color: '#2563EB' },
  { key: 'bus', label: 'Bus', color: '#10B981' },
  { key: 'truck', label: 'Camion', color: '#F59E0B' },
  { key: 'motorcycle', label: 'Moto', color: '#A855F7' },
  { key: 'person', label: 'Pieton', color: '#6B7280' },
];
