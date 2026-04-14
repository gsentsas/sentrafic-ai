'use client';

import { Truck, Radio, AlertCircle, Building2, Activity } from 'lucide-react';
import { PageShell } from '@/components/layout/page-shell';
import { KPICard } from '@/components/cards/kpi-card';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { AlertCard } from '@/components/cards/alert-card';
import { TrafficLineChart } from '@/components/charts/traffic-line-chart';
import { useOverview } from '@/hooks/use-overview';
import { formatNumber, formatCongestion, timeAgo } from '@/lib/format';
import { CLASS_LABELS } from '@/lib/constants';

export default function OverviewPage() {
  const { data, loading, error, refetch } = useOverview();

  if (loading) {
    return (
      <PageShell title="Tableau de bord">
        <LoadingState />
      </PageShell>
    );
  }

  if (error || !data) {
    return (
      <PageShell title="Tableau de bord">
        <ErrorState
          message={error?.message || 'Echec du chargement des donnees'}
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  const chartData = data.traffic_trend_24h.map((point) => ({
    timestamp: point.timestamp.split('T')[1]?.substring(0, 5) || point.timestamp,
    count: point.count,
  }));

  return (
    <PageShell
      title="Tableau de bord"
      notificationCount={data.summary.alerts_unresolved}
    >
      {/* Indicateurs cles */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard
          icon={Truck}
          label="Vehicules aujourd'hui"
          value={data.summary.total_vehicles_today}
          color="blue"
        />
        <KPICard
          icon={Radio}
          label="Cameras en ligne"
          value={data.summary.cameras_online}
          color="green"
        />
        <KPICard
          icon={AlertCircle}
          label="Alertes non resolues"
          value={data.summary.alerts_unresolved}
          color="red"
        />
        <KPICard
          icon={Building2}
          label="Sites surveilles"
          value={data.summary.total_sites}
          color="amber"
        />
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <TrafficLineChart
            data={chartData}
            title="Tendance du trafic (24 heures)"
          />
        </div>

        {/* Resume congestion */}
        <Card>
          <h3 className="subsection-title">Congestion actuelle</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Niveau moyen</span>
              <Badge
                variant={data.congestion.avg_level === 'heavy' || data.congestion.avg_level === 'blocked' ? 'danger' : data.congestion.avg_level === 'moderate' ? 'warning' : 'success'}
              >
                {formatCongestion(data.congestion.avg_level)}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Vehicules (1h)</span>
              <span className="font-semibold text-gray-900">{formatNumber(data.congestion.total_vehicles_1h)}</span>
            </div>
            {data.congestion.by_class && Object.entries(data.congestion.by_class).length > 0 && (
              <div className="pt-3 border-t">
                <p className="text-xs text-gray-500 mb-2">Par classe (1h)</p>
                {Object.entries(data.congestion.by_class).map(([cls, count]) => (
                  <div key={cls} className="flex items-center justify-between py-1">
                    <span className="text-sm text-gray-600">{CLASS_LABELS[cls] || cls}</span>
                    <span className="text-sm font-medium text-gray-900">{formatNumber(count as number)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Cameras a surveiller */}
      {data.watchlist && data.watchlist.length > 0 && (
        <div className="mb-8">
          <h2 className="subsection-title mb-4">Cameras a surveiller</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.watchlist.map((cam) => (
              <Card key={cam.camera_id} className="border-l-4 border-l-red-400">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{cam.camera_name}</p>
                    <p className="text-xs text-gray-500">
                      {cam.last_seen_at ? timeAgo(cam.last_seen_at) : 'Jamais vu'}
                    </p>
                  </div>
                  <Badge variant={cam.status === 'error' ? 'danger' : 'default'}>
                    {cam.status === 'error' ? 'Erreur' : 'Hors ligne'}
                  </Badge>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Alertes recentes */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="subsection-title">Alertes recentes</h2>
          <Badge variant="danger">{data.summary.alerts_unresolved} non resolues</Badge>
        </div>

        {data.recent_alerts.length > 0 ? (
          <div className="space-y-3">
            {data.recent_alerts.slice(0, 5).map((alert) => (
              <AlertCard
                key={alert.id}
                {...alert}
              />
            ))}
          </div>
        ) : (
          <Card>
            <div className="text-center py-8">
              <Activity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-600">Aucune alerte pour le moment</p>
            </div>
          </Card>
        )}
      </div>
    </PageShell>
  );
}
