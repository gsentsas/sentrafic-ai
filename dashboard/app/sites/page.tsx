'use client';

import { Plus } from 'lucide-react';
import { PageShell } from '@/components/layout/page-shell';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { EmptyState } from '@/components/ui/empty-state';
import { SitesTable } from '@/components/tables/sites-table';
import { useSites } from '@/hooks/use-sites';
import { MapPin } from 'lucide-react';

export default function SitesPage() {
  const { sites, loading, error, refetch } = useSites();

  if (loading) {
    return (
      <PageShell title="Sites">
        <LoadingState />
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell title="Sites">
        <ErrorState
          message={error.message}
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  return (
    <PageShell title="Sites">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {sites.length} {sites.length === 1 ? 'Site' : 'Sites'}
          </h2>
          <p className="text-gray-600">Manage your traffic monitoring sites</p>
        </div>
        <Button variant="primary">
          <Plus className="w-4 h-4 mr-2" />
          Add Site
        </Button>
      </div>

      {sites.length > 0 ? (
        <SitesTable sites={sites} />
      ) : (
        <Card>
          <EmptyState
            icon={MapPin}
            title="No sites yet"
            description="Create your first monitoring site to start tracking traffic"
            actionLabel="Add Site"
          />
        </Card>
      )}
    </PageShell>
  );
}
