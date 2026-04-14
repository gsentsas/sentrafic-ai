'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { PageShell } from '@/components/layout/page-shell';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { TrafficLineChart } from '@/components/charts/traffic-line-chart';
import { DistributionPieChart } from '@/components/charts/distribution-pie-chart';
import { getCameraById, getCameraTraffic } from '@/lib/api';
import { Camera, CameraTrafficData, ClassDistribution } from '@/lib/types';
import {
  ALERT_TYPE_LABELS,
  CONGESTION_LABELS,
  CAMERA_STATUS_LABELS,
  CAMERA_HEALTH_LABELS,
  CLASS_LABELS,
} from '@/lib/constants';
import { formatNumber, timeAgo } from '@/lib/format';
import {
  Radio,
  AlertCircle,
  Truck,
  Activity,
  ArrowLeft,
  RefreshCw,
} from 'lucide-react';

function StatusBadge({ status }: { status: string }) {
  const variant =
    status === 'online' ? 'success' : status === 'error' ? 'danger' : 'default';
  return (
    <Badge variant={variant}>
      {CAMERA_STATUS_LABELS[status] || status}
    </Badge>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const variant =
    severity === 'critical' ? 'danger' : severity === 'warning' ? 'warning' : 'default';
  return <Badge variant={variant}>{severity}</Badge>;
}

export default function CameraDetailPage() {
  const params = useParams();
  const router = useRouter();
  const cameraId = params?.id as string;

  const [camera, setCamera] = useState<Camera | null>(null);
  const [traffic, setTraffic] = useState<CameraTrafficData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!cameraId) return;
    try {
      const [cam, traf] = await Promise.all([
        getCameraById(cameraId),
        getCameraTraffic(cameraId, 24),
      ]);
      setCamera(cam);
      setTraffic(traf);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Echec du chargement'));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [cameraId]);

  useEffect(() => {
    load();
    // Auto-refresh every 30s
    const interval = setInterval(load, 30_000);
    return () => clearInterval(interval);
  }, [load]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await load();
  };

  if (loading) {
    return (
      <PageShell title="Camera">
        <LoadingState />
      </PageShell>
    );
  }

  if (error || !camera || !traffic) {
    return (
      <PageShell title="Camera">
        <ErrorState
          message={error?.message || 'Camera introuvable'}
          onRetry={load}
        />
      </PageShell>
    );
  }

  const trendData = (traffic.trend || []).map((point) => ({
    timestamp: point.timestamp.split('T')[1]?.substring(0, 5) || point.timestamp,
    count: point.count,
  }));

  // DistributionPieChart expects ClassDistribution[]
  const distributionData: ClassDistribution[] = traffic.distribution?.distribution
    ? [traffic.distribution as unknown as ClassDistribution]
    : [];

  const lastReading = traffic.last_reading;
  const summary = traffic.summary || {};

  return (
    <PageShell
      title={camera.name}
      breadcrumb={`Cameras / ${camera.name}`}
    >
      {/* Header actions */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => router.push('/cameras')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" />
            Retour aux cameras
          </Button>
          <StatusBadge status={camera.status} />
          <Badge variant="default">
            {CAMERA_HEALTH_LABELS[camera.health_label || 'unknown'] || camera.health_label}
          </Badge>
        </div>
        <Button
          variant="ghost"
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Actualiser
        </Button>
      </div>

      {/* Camera info */}
      <Card className="mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Localisation</p>
            <p className="text-sm font-medium text-gray-900">
              {camera.location_description || '—'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Derniere vue</p>
            <p className="text-sm font-medium text-gray-900">
              {camera.last_seen_at ? timeAgo(camera.last_seen_at) : 'Jamais'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Site</p>
            <p className="text-sm font-medium text-gray-900">
              {camera.site_name || '—'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">URL de flux</p>
            <p className="text-sm font-mono text-gray-600 truncate max-w-[200px]" title={camera.stream_url}>
              {camera.stream_url || '—'}
            </p>
          </div>
        </div>
      </Card>

      {/* KPI row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-50">
              <Truck className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Vehicules (1h)</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(summary.total_vehicles || 0)}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-50">
              <Activity className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Congestion</p>
              <p className="text-lg font-bold text-gray-900">
                {CONGESTION_LABELS[summary.avg_congestion_level || 'free'] || summary.avg_congestion_level || '—'}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-50">
              <Radio className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Occupation</p>
              <p className="text-2xl font-bold text-gray-900">
                {lastReading ? `${(lastReading.avg_occupancy * 100).toFixed(0)}%` : '—'}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-50">
              <AlertCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Alertes actives</p>
              <p className="text-2xl font-bold text-gray-900">
                {traffic.recent_alerts?.filter((a) => !a.is_resolved).length ?? 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2">
          <TrafficLineChart
            data={trendData}
            title="Volume de trafic (24 heures)"
          />
        </div>

        {distributionData.length > 0 ? (
          <DistributionPieChart
            data={distributionData}
            title="Repartition par classe"
          />
        ) : (
          <Card>
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Repartition par classe</h3>
            <div className="h-40 flex items-center justify-center text-gray-400 text-sm">
              Pas encore de donnees
            </div>
          </Card>
        )}
      </div>

      {/* Vehicle class breakdown + Recent alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Class breakdown from summary */}
        <Card header={
          <h3 className="font-semibold text-gray-900">Comptage par classe (1h)</h3>
        }>
          {summary.by_class && Object.keys(summary.by_class).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(summary.by_class).map(([cls, count]) => (
                <div key={cls} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">
                    {CLASS_LABELS[cls] || cls}
                  </span>
                  <div className="flex items-center gap-3">
                    <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-2 bg-blue-500 rounded-full"
                        style={{
                          width: `${summary.total_vehicles ? ((count as number) / summary.total_vehicles) * 100 : 0}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-10 text-right">
                      {formatNumber(count as number)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">Aucune donnee disponible</p>
          )}
        </Card>

        {/* Recent alerts */}
        <Card header={
          <h3 className="font-semibold text-gray-900">Alertes recentes</h3>
        }>
          {traffic.recent_alerts && traffic.recent_alerts.length > 0 ? (
            <div className="space-y-3">
              {traffic.recent_alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-start justify-between gap-3 py-2 border-b border-gray-50 last:border-0"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {ALERT_TYPE_LABELS[alert.alert_type] || alert.alert_type}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {alert.created_at ? timeAgo(alert.created_at) : '—'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <SeverityBadge severity={alert.severity} />
                    {alert.is_resolved && (
                      <Badge variant="success">Resolu</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">Aucune alerte pour cette camera</p>
          )}
        </Card>
      </div>
    </PageShell>
  );
}
