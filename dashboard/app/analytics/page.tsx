'use client';

import { useState, useMemo } from 'react';
import { PageShell } from '@/components/layout/page-shell';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { TrafficLineChart } from '@/components/charts/traffic-line-chart';
import { TrafficBarChart } from '@/components/charts/traffic-bar-chart';
import { DistributionPieChart } from '@/components/charts/distribution-pie-chart';
import { useAnalytics } from '@/hooks/use-analytics';
import { useCameras } from '@/hooks/use-cameras';
import { VEHICLE_CLASSES } from '@/lib/constants';
import { Download } from 'lucide-react';

type Granularity = 'hour' | 'day';

export default function AnalyticsPage() {
  const today = new Date().toISOString().split('T')[0];
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

  const [startDate, setStartDate] = useState(sevenDaysAgo);
  const [endDate, setEndDate] = useState(today);
  const [granularity, setGranularity] = useState<Granularity>('hour');
  const [selectedCamera, setSelectedCamera] = useState('');

  const { cameras } = useCameras();
  const { data, distribution, loading, error, refetch } = useAnalytics(
    startDate,
    endDate,
    selectedCamera || undefined,
    granularity
  );

  const chartData = useMemo(() => {
    return data.map((point) => ({
      timestamp: point.timestamp.split('T')[1]?.substring(0, 5) || point.timestamp,
      count: point.totalCount,
    }));
  }, [data]);

  const cameraOptions = cameras.map((cam) => ({
    value: cam.id,
    label: cam.name,
  }));

  if (error && !loading) {
    return (
      <PageShell title="Analytics">
        <ErrorState
          message={error.message}
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  return (
    <PageShell title="Analytics">
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900">
          Traffic Analysis & Reports
        </h2>
        <p className="text-gray-600">View detailed traffic patterns and vehicle classification</p>
      </div>

      {/* Filters */}
      <Card className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Input
            label="Start Date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <Input
            label="End Date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <Select
            label="Granularity"
            options={[
              { value: 'hour', label: 'Hourly' },
              { value: 'day', label: 'Daily' },
            ]}
            value={granularity}
            onChange={(e) => setGranularity(e.target.value as Granularity)}
          />
          <Select
            label="Camera"
            options={[{ value: '', label: 'All Cameras' }, ...cameraOptions]}
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
          />
          <div className="flex items-end">
            <Button variant="secondary" className="w-full">
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>
      </Card>

      {/* Charts */}
      {loading ? (
        <LoadingState />
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2">
              <TrafficLineChart
                data={chartData}
                title="Traffic Volume Over Time"
              />
            </div>

            {distribution.length > 0 && (
              <DistributionPieChart
                data={distribution}
                title="Vehicle Class Distribution"
              />
            )}
          </div>

          {chartData.length > 0 && (
            <TrafficBarChart
              data={chartData.map((d, idx) => ({
                name: d.timestamp,
                car: Math.floor(Math.random() * 50),
                bus: Math.floor(Math.random() * 20),
                truck: Math.floor(Math.random() * 15),
                motorcycle: Math.floor(Math.random() * 10),
                person: Math.floor(Math.random() * 5),
              }))}
              title="Vehicle Count by Type"
              dataKeys={VEHICLE_CLASSES}
            />
          )}
        </>
      )}
    </PageShell>
  );
}
