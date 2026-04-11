'use client';

import { PageShell } from '@/components/layout/page-shell';
import { Card } from '@/components/ui/card';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { EmptyState } from '@/components/ui/empty-state';
import { LiveCameraTile } from '@/components/live/live-camera-tile';
import { useCameras } from '@/hooks/use-cameras';
import { Radio } from 'lucide-react';

export default function LivePage() {
  const { cameras, loading, error, refetch } = useCameras();

  if (loading) {
    return (
      <PageShell title="Live Monitoring">
        <LoadingState />
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell title="Live Monitoring">
        <ErrorState
          message={error.message}
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  return (
    <PageShell title="Live Monitoring">
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900">
          {cameras.length} {cameras.length === 1 ? 'Camera' : 'Cameras'} Active
        </h2>
        <p className="text-gray-600">Real-time view of all monitoring cameras</p>
      </div>

      {cameras.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((camera) => (
            <LiveCameraTile
              key={camera.id}
              cameraName={camera.name}
              siteName={camera.siteName}
              status={camera.status}
              vehicleCount={0}
              congestionLevel="free"
            />
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={Radio}
            title="No cameras available"
            description="Add cameras to start live monitoring"
          />
        </Card>
      )}
    </PageShell>
  );
}
