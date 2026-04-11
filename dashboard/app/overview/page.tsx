'use client';

import { Truck, Radio, AlertCircle, Building2, Activity, BarChart3 } from 'lucide-react';
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
import { CONGESTION_COLORS } from '@/lib/constants';

export default function OverviewPage() {
  const { data, loading, error, refetch } = useOverview();

  if (loading) {
    return (
      <PageShell title="Overview">
        <LoadingState />
      </PageShell>
    );
  }

  if (error || !data) {
    return (
      <PageShell title="Overview">
        <ErrorState
          message={error?.message || 'Failed to load dashboard data'}
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  const chartData = data.trafficTrend24h.map((point) => ({
    timestamp: point.timestamp.split('T')[1]?.substring(0, 5) || point.timestamp,
    count: point.count,
  }));

  return (
    <PageShell
      title="Dashboard Overview"
      notificationCount={data.alertsUnresolved}
    >
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard
          icon={Truck}
          label="Total Vehicles Today"
          value={data.totalVehiclesToday}
          color="blue"
        />
        <KPICard
          icon={Radio}
          label="Active Cameras"
          value={data.camerasOnline}
          color="green"
        />
        <KPICard
          icon={AlertCircle}
          label="Unresolved Alerts"
          value={data.alertsUnresolved}
          color="red"
        />
        <KPICard
          icon={Building2}
          label="Sites Monitored"
          value={data.totalSites}
          color="amber"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <TrafficLineChart
            data={chartData}
            title="Traffic Trend (24 Hours)"
          />
        </div>

        {/* Congestion Summary */}
        <Card>
          <h3 className="subsection-title">Congestion Summary</h3>
          <div className="space-y-3">
            {[
              { label: 'Free', value: data.congestionSummary.free, level: 'free' },
              { label: 'Moderate', value: data.congestionSummary.moderate, level: 'moderate' },
              { label: 'Heavy', value: data.congestionSummary.heavy, level: 'heavy' },
              { label: 'Blocked', value: data.congestionSummary.blocked, level: 'blocked' },
            ].map((item) => (
              <div key={item.level} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{
                      backgroundColor: CONGESTION_COLORS[item.level as keyof typeof CONGESTION_COLORS],
                    }}
                  />
                  <span className="text-sm text-gray-600">{item.label}</span>
                </div>
                <span className="font-semibold text-gray-900">{formatNumber(item.value)}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Recent Alerts */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="subsection-title">Recent Alerts</h2>
          <Badge variant="danger">{data.recentAlerts.length} unresolved</Badge>
        </div>

        {data.recentAlerts.length > 0 ? (
          <div className="space-y-3">
            {data.recentAlerts.slice(0, 5).map((alert) => (
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
              <p className="text-gray-600">No alerts at the moment</p>
            </div>
          </Card>
        )}
      </div>
    </PageShell>
  );
}
