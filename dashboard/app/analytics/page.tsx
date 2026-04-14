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
import { exportTrafficCsv, downloadBlob } from '@/lib/api';
import { Download, Loader2 } from 'lucide-react';

type Granularity = 'hour' | 'day';

export default function AnalyticsPage() {
  const today = new Date().toISOString().split('T')[0];
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

  const [startDate, setStartDate] = useState(sevenDaysAgo);
  const [endDate, setEndDate] = useState(today);
  const [granularity, setGranularity] = useState<Granularity>('hour');
  const [selectedCamera, setSelectedCamera] = useState('');
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState('');

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
      count: point.total_count,
    }));
  }, [data]);

  const barChartData = useMemo(() => {
    return data.map((point) => ({
      name: point.timestamp.split('T')[1]?.substring(0, 5) || point.timestamp,
      car: point.car_count,
      bus: point.bus_count,
      truck: point.truck_count,
      motorcycle: point.motorcycle_count,
      person: point.person_count,
    }));
  }, [data]);

  const cameraOptions = cameras.map((cam) => ({ value: cam.id, label: cam.name }));

  const handleExport = async () => {
    setExporting(true);
    setExportError('');
    try {
      const blob = await exportTrafficCsv(
        startDate,
        endDate,
        selectedCamera || undefined
      );
      const cam = cameras.find((c) => c.id === selectedCamera);
      const filename = `trafic_${startDate}_${endDate}${cam ? `_${cam.name.replace(/\s+/g, '_')}` : ''}.csv`;
      downloadBlob(blob, filename);
    } catch (e: any) {
      setExportError(e.message || "Échec de l'export. Veuillez réessayer.");
    } finally {
      setExporting(false);
    }
  };

  if (error && !loading) {
    return (
      <PageShell title="Analytique">
        <ErrorState
          message="Impossible de charger les données analytiques. Vérifiez les filtres et réessayez."
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  return (
    <PageShell title="Analytique">
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900">
          Analyse du trafic et rapports
        </h2>
        <p className="text-gray-500">
          Visualisez les tendances de trafic et la classification des véhicules
        </p>
      </div>

      {/* Filtres */}
      <Card className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Input
            label="Date de début"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <Input
            label="Date de fin"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <Select
            label="Granularité"
            options={[
              { value: 'hour', label: 'Par heure' },
              { value: 'day', label: 'Par jour' },
            ]}
            value={granularity}
            onChange={(e) => setGranularity(e.target.value as Granularity)}
          />
          <Select
            label="Caméra"
            options={[{ value: '', label: 'Toutes les caméras' }, ...cameraOptions]}
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
          />
          <div className="flex flex-col justify-end gap-1">
            <Button
              variant="secondary"
              onClick={handleExport}
              disabled={exporting}
              className="w-full"
            >
              {exporting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Export...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Exporter CSV
                </>
              )}
            </Button>
            {exportError && (
              <p className="text-xs text-red-600">{exportError}</p>
            )}
          </div>
        </div>
      </Card>

      {/* Graphiques */}
      {loading ? (
        <LoadingState message="Chargement des données analytiques..." />
      ) : data.length === 0 ? (
        <Card>
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg font-medium mb-1">Aucune donnée sur cette période</p>
            <p className="text-sm">Modifiez les dates ou la caméra sélectionnée.</p>
          </div>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2">
              <TrafficLineChart
                data={chartData}
                title="Volume de trafic dans le temps"
              />
            </div>

            {distribution.length > 0 && (
              <DistributionPieChart
                data={distribution}
                title="Répartition par classe"
              />
            )}
          </div>

          {barChartData.length > 0 && (
            <TrafficBarChart
              data={barChartData}
              title="Comptage par type de véhicule"
              dataKeys={VEHICLE_CLASSES}
            />
          )}
        </>
      )}
    </PageShell>
  );
}
