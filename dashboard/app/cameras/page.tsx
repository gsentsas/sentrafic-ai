'use client';

import { useState } from 'react';
import { Plus } from 'lucide-react';
import { PageShell } from '@/components/layout/page-shell';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { EmptyState } from '@/components/ui/empty-state';
import { CamerasTable } from '@/components/tables/cameras-table';
import { useCameras } from '@/hooks/use-cameras';
import { useSites } from '@/hooks/use-sites';
import { Camera as CameraIcon } from 'lucide-react';

export default function CamerasPage() {
  const [selectedSite, setSelectedSite] = useState('');
  const { cameras, loading, error, refetch } = useCameras(selectedSite || undefined);
  const { sites } = useSites();

  const siteOptions = sites.map((site) => ({
    value: site.id,
    label: site.name,
  }));

  if (loading) {
    return (
      <PageShell title="Cameras">
        <LoadingState />
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell title="Cameras">
        <ErrorState
          message={error.message}
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  return (
    <PageShell title="Cameras">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {cameras.length} {cameras.length === 1 ? 'Camera' : 'Cameras'}
          </h2>
          <p className="text-gray-600">Monitor and manage your camera feeds</p>
        </div>
        <Button variant="primary">
          <Plus className="w-4 h-4 mr-2" />
          Add Camera
        </Button>
      </div>

      {/* Filter */}
      <div className="mb-6 max-w-xs">
        <Select
          label="Filter by Site"
          options={[{ value: '', label: 'All Sites' }, ...siteOptions]}
          value={selectedSite}
          onChange={(e) => setSelectedSite(e.target.value)}
          placeholder="All Sites"
        />
      </div>

      {cameras.length > 0 ? (
        <CamerasTable cameras={cameras} />
      ) : (
        <Card>
          <EmptyState
            icon={CameraIcon}
            title="No cameras yet"
            description="Add a camera to start monitoring traffic"
            actionLabel="Add Camera"
          />
        </Card>
      )}
    </PageShell>
  );
}
