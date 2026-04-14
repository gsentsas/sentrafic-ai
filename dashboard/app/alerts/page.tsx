'use client';

import { useState } from 'react';
import { PageShell } from '@/components/layout/page-shell';
import { Select } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { EmptyState } from '@/components/ui/empty-state';
import { AlertsTable } from '@/components/tables/alerts-table';
import { useAlerts } from '@/hooks/use-alerts';
import { AlertCircle } from 'lucide-react';

export default function AlertsPage() {
  const [severityFilter, setSeverityFilter] = useState('');
  const [resolvedFilter, setResolvedFilter] = useState('false');

  const isResolved = resolvedFilter === 'true' ? true : resolvedFilter === 'false' ? false : undefined;
  const { alerts, loading, error, refetch, resolveAlert, total } = useAlerts(
    0,
    100,
    severityFilter || undefined,
    isResolved
  );

  const [resolvingId, setResolvingId] = useState<string | null>(null);

  const handleResolve = async (alertId: string) => {
    setResolvingId(alertId);
    try {
      await resolveAlert(alertId);
    } finally {
      setResolvingId(null);
    }
  };

  if (loading) {
    return (
      <PageShell title="Alertes">
        <LoadingState />
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell title="Alertes">
        <ErrorState
          message={error.message}
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  return (
    <PageShell title="Alertes">
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900">
          {total} {total === 1 ? 'Alerte' : 'Alertes'}
        </h2>
        <p className="text-gray-600">Surveillance et gestion des alertes trafic</p>
      </div>

      {/* Filtres */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 max-w-md">
        <Select
          label="Severite"
          options={[
            { value: '', label: 'Toutes' },
            { value: 'info', label: 'Info' },
            { value: 'warning', label: 'Avertissement' },
            { value: 'critical', label: 'Critique' },
          ]}
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
        />
        <Select
          label="Statut"
          options={[
            { value: 'false', label: 'Non resolues' },
            { value: 'true', label: 'Resolues' },
            { value: '', label: 'Toutes' },
          ]}
          value={resolvedFilter}
          onChange={(e) => setResolvedFilter(e.target.value)}
        />
      </div>

      {alerts.length > 0 ? (
        <AlertsTable
          alerts={alerts}
          onResolve={handleResolve}
          resolvingId={resolvingId}
        />
      ) : (
        <Card>
          <EmptyState
            icon={AlertCircle}
            title="Aucune alerte"
            description="Le systeme fonctionne normalement, aucune alerte active"
          />
        </Card>
      )}
    </PageShell>
  );
}
