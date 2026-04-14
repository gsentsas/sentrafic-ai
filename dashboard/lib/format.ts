import { CLASS_LABELS, CONGESTION_LABELS } from './constants';

export const formatNumber = (num: number | null | undefined): string => {
  if (num === null || num === undefined) return '0';
  return new Intl.NumberFormat('fr-FR').format(Math.floor(num));
};

export const formatDate = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatTime = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

export const formatDateTime = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleString('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${(value).toFixed(decimals)} %`;
};

export const formatCongestion = (level: string): string => {
  return CONGESTION_LABELS[level] || level.charAt(0).toUpperCase() + level.slice(1);
};

export const timeAgo = (dateString: string | Date): string => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  let interval = seconds / 31536000;
  if (interval > 1) return 'il y a ' + Math.floor(interval) + ' an' + (Math.floor(interval) > 1 ? 's' : '');

  interval = seconds / 2592000;
  if (interval > 1) return 'il y a ' + Math.floor(interval) + ' mois';

  interval = seconds / 86400;
  if (interval > 1) return 'il y a ' + Math.floor(interval) + ' j';

  interval = seconds / 3600;
  if (interval > 1) return 'il y a ' + Math.floor(interval) + ' h';

  interval = seconds / 60;
  if (interval > 1) return 'il y a ' + Math.floor(interval) + ' min';

  if (seconds < 10) return 'a l\'instant';
  return 'il y a ' + Math.floor(seconds) + ' s';
};

export const classLabel = (className: string): string => {
  return CLASS_LABELS[className.toLowerCase()] || className;
};
