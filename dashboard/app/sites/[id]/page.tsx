'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Camera, MapPin } from 'lucide-react';
import { PageShell } from '@/components/layout/page-shell';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { getSiteById } from '@/lib/api';
import { Site } from '@/lib/types';
import { formatDate } from '@/lib/format';
import { useCameras } from '@/hooks/use-cameras';

export default function SiteDetailPage() {
  const params = useParams();
  const router = useRouter();
  const siteId = params?.id as string;
  const [site, setSite] = useState<Site | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { cameras, loading: camerasLoading } = useCameras(siteId);

  const loadSite = useCallback(async () => {
    if (!siteId) return;
    try {
      const result = await getSiteById(siteId);
      setSite(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Echec du chargement du site'));
    } finally {
      setLoading(false);
    }
  }, [siteId]);

  useEffect(() => {
    loadSite();
  }, [loadSite]);

  if (loading) {
    return (
      <PageShell title="Site">
        <LoadingState message="Chargement du site..." />
      </PageShell>
    );
  }

  if (error || !site) {
    return (
      <PageShell title="Site">
        <ErrorState message={error?.message || 'Site introuvable'} onRetry={loadSite} />
      </PageShell>
    );
  }

  return (
    <PageShell title={site.name} breadcrumb={`Sites / ${site.name}`}>
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="ghost"
          onClick={() => router.push('/sites')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour aux sites
        </Button>
        <Badge variant={site.is_active ? 'success' : 'default'}>
          {site.is_active ? 'Actif' : 'Inactif'}
        </Badge>
      </div>

      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Ville</p>
            <p className="text-sm font-medium text-gray-900">{site.city}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Adresse</p>
            <p className="text-sm font-medium text-gray-900">{site.address}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Type</p>
            <p className="text-sm font-medium text-gray-900">{site.site_type}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Coordonnees</p>
            <p className="text-sm font-medium text-gray-900">
              {site.latitude}, {site.longitude}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Cameras</p>
            <p className="text-sm font-medium text-gray-900">{site.camera_count}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Cree le</p>
            <p className="text-sm font-medium text-gray-900">{formatDate(site.created_at)}</p>
          </div>
        </div>
      </Card>

      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Camera className="w-4 h-4 text-gray-500" />
          <h3 className="font-semibold text-gray-900">Cameras du site</h3>
        </div>
        {camerasLoading ? (
          <LoadingState message="Chargement des cameras..." />
        ) : cameras.length === 0 ? (
          <div className="text-sm text-gray-500 flex items-center gap-2">
            <MapPin className="w-4 h-4" />
            Aucune camera configuree pour ce site.
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {cameras.map((camera) => (
              <div key={camera.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{camera.name}</p>
                  <p className="text-xs text-gray-500">{camera.stream_url}</p>
                </div>
                <Link href={`/cameras/${camera.id}`} className="text-sm text-blue-600 hover:text-blue-700">
                  Ouvrir
                </Link>
              </div>
            ))}
          </div>
        )}
      </Card>
    </PageShell>
  );
}
