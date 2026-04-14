'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Camera, Activity, Clock } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getCameraTraffic } from '@/lib/api';
import { CameraTrafficData } from '@/lib/types';
import { CONGESTION_COLORS, VEHICLE_CLASSES } from '@/lib/constants';
import { formatCongestion, timeAgo } from '@/lib/format';

interface LiveCameraTileProps {
  cameraId: string;
  cameraName: string;
  siteName: string | null;
  streamUrl: string;
  status: 'online' | 'offline' | 'error';
  lastSeenAt: string | null;
  selected?: boolean;
  onToggleLive?: (cameraId: string) => void;
  trafficSnapshot?: {
    total_count: number;
    congestion_level: string;
    avg_occupancy: number;
    timestamp: string | null;
    is_stale?: boolean;
  } | null;
}

const statusVariants: Record<string, 'success' | 'default' | 'danger'> = {
  online: 'success',
  offline: 'default',
  error: 'danger',
};

const statusLabels: Record<string, string> = {
  online: 'EN LIGNE',
  offline: 'HORS LIGNE',
  error: 'ERREUR',
};

const STALE_THRESHOLD_MS = 30_000;

// Considère les données "fraîches" si elles datent de moins de 30 secondes
const isLive = (timestamp: string | null): boolean => {
  if (!timestamp) return false;
  return Date.now() - new Date(timestamp).getTime() < STALE_THRESHOLD_MS;
};

export const LiveCameraTile = ({
  cameraId,
  cameraName,
  siteName,
  streamUrl,
  status,
  lastSeenAt,
  selected = false,
  onToggleLive,
  trafficSnapshot = null,
}: LiveCameraTileProps) => {
  const [traffic, setTraffic] = useState<CameraTrafficData | null>(null);
  const [liveStatus, setLiveStatus] = useState(false);

  const fetchTraffic = useCallback(async () => {
    try {
      const data = await getCameraTraffic(cameraId, 1); // dernière heure
      setTraffic(data);
      // "LIVE" si la caméra a envoyé des données dans les 30 dernières secondes
      setLiveStatus(isLive(data.last_seen_at));
    } catch {
      // silencieux : on garde les dernières données
    }
  }, [cameraId]);

  useEffect(() => {
    if (trafficSnapshot) return;
    fetchTraffic();
    const interval = setInterval(fetchTraffic, 10_000); // refresh toutes les 10s
    return () => clearInterval(interval);
  }, [fetchTraffic, trafficSnapshot]);

  const lastReading = trafficSnapshot ?? traffic?.last_reading;
  const vehicleCount = lastReading?.total_count ?? 0;
  const congestion = (lastReading?.congestion_level ?? 'free') as keyof typeof CONGESTION_COLORS;
  const occupancy = lastReading?.avg_occupancy ?? 0;
  const distribution = traffic?.distribution?.distribution ?? {};
  const totalDist = Object.values(distribution).reduce((a, b) => a + b, 0);
  const seenAt = traffic?.last_seen_at ?? lastSeenAt;
  const readingTimestamp = lastReading?.timestamp ?? seenAt;
  const stale = useMemo(() => {
    if (typeof lastReading?.is_stale === 'boolean') return lastReading.is_stale;
    if (!readingTimestamp) return true;
    return Date.now() - new Date(readingTimestamp).getTime() >= STALE_THRESHOLD_MS;
  }, [lastReading?.is_stale, readingTimestamp]);

  useEffect(() => {
    setLiveStatus(isLive(readingTimestamp));
  }, [readingTimestamp]);

  return (
    <button
      type="button"
      onClick={() => onToggleLive?.(cameraId)}
      className="block w-full text-left"
    >
      <Card
        className={`overflow-hidden hover:shadow-lg transition-shadow duration-200 cursor-pointer ${
          selected ? 'ring-2 ring-blue-500 shadow-lg' : ''
        }`}
      >
      {/* Zone visuelle caméra */}
      <div className="relative bg-gray-900 aspect-video flex items-center justify-center select-none">
        <Camera className="w-14 h-14 text-gray-600" />

        {/* Badge statut caméra */}
        <div className="absolute top-3 left-3">
          <Badge variant={statusVariants[status]}>
            {statusLabels[status] ?? status.toUpperCase()}
          </Badge>
        </div>

        {/* Badge LIVE animé */}
        {liveStatus && (
          <div className="absolute top-3 right-3 flex items-center gap-1.5 bg-black/60 rounded-full px-2.5 py-1">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-xs font-bold text-white tracking-widest">LIVE</span>
          </div>
        )}

        {status === 'online' && stale && (
          <div className="absolute top-3 right-3 flex items-center gap-1.5 bg-amber-500/90 rounded-full px-2.5 py-1">
            <span className="w-2 h-2 rounded-full bg-white/90" />
            <span className="text-xs font-bold text-white tracking-widest">PERIME</span>
          </div>
        )}

        {/* Indicateur congestion (coin bas-droit) */}
        {status === 'online' && (
          <div className="absolute bottom-3 right-3 flex items-center gap-1.5">
            <span
              className="w-3 h-3 rounded-full animate-pulse"
              style={{ backgroundColor: CONGESTION_COLORS[congestion] }}
            />
            <span className="text-xs text-white/80 font-medium">
              {formatCongestion(congestion)}
            </span>
          </div>
        )}

        {/* Occupancy bar en bas */}
        {status === 'online' && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-700">
            <div
              className="h-full transition-all duration-500"
              style={{
                width: `${Math.round(occupancy * 100)}%`,
                backgroundColor: CONGESTION_COLORS[congestion],
              }}
            />
          </div>
        )}
      </div>

      {/* Section infos */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-1">
          <h3 className="font-semibold text-gray-900 truncate pr-2">{cameraName}</h3>
          <Activity className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
        </div>
        <p className="text-sm text-gray-500 truncate mb-3">{siteName ?? '—'}</p>

        {/* Stats comptage + occupancy */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="bg-gray-50 rounded-lg p-2.5">
            <p className="text-xs text-gray-500 mb-0.5">Véhicules (1h)</p>
            <p className="text-xl font-bold text-gray-900">{vehicleCount.toLocaleString()}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-2.5">
            <p className="text-xs text-gray-500 mb-0.5">Occupation</p>
            <p
              className="text-xl font-bold"
              style={{ color: CONGESTION_COLORS[congestion] }}
            >
              {Math.round(occupancy * 100)}%
            </p>
          </div>
        </div>

        {/* Mini-barres de distribution */}
        {totalDist > 0 && (
          <div className="mb-3">
            <p className="text-xs text-gray-500 mb-1.5">Distribution</p>
            <div className="flex gap-1 h-6 rounded overflow-hidden">
              {VEHICLE_CLASSES.map(({ key, color }) => {
                const count = distribution[key] ?? 0;
                const pct = totalDist > 0 ? (count / totalDist) * 100 : 0;
                if (pct < 1) return null;
                return (
                  <div
                    key={key}
                    title={`${key}: ${Math.round(pct)}%`}
                    className="transition-all duration-500"
                    style={{ width: `${pct}%`, backgroundColor: color }}
                  />
                );
              })}
            </div>
            <div className="flex gap-3 mt-1.5 flex-wrap">
              {VEHICLE_CLASSES.map(({ key, color, label }) => {
                const count = distribution[key] ?? 0;
                if (!count) return null;
                return (
                  <span key={key} className="flex items-center gap-1 text-xs text-gray-500">
                    <span
                      className="w-2 h-2 rounded-full flex-shrink-0"
                      style={{ backgroundColor: color }}
                    />
                    {label}: {count}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Dernière activité */}
        <div className="flex items-center gap-1.5 text-xs text-gray-400">
          <Clock className="w-3.5 h-3.5" />
          {seenAt
            ? `Mis à jour ${timeAgo(seenAt)}`
            : 'Aucune donnée récente'}
        </div>
      </div>
        <div className="px-4 pb-4 -mt-1">
          <p className="text-xs text-blue-600 font-medium truncate">
            {selected ? 'Retirer du mur live' : 'Ajouter au mur live'}: {streamUrl}
          </p>
        </div>
      </Card>
    </button>
  );
};
