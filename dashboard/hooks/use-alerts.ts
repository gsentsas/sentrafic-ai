'use client';

import { useState, useEffect, useCallback } from 'react';
import { Alert, PaginatedResponse } from '@/lib/types';
import { getAlerts, resolveAlert as apiResolveAlert } from '@/lib/api';

interface UseAlertsResult {
  alerts: Alert[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  resolveAlert: (alertId: string) => Promise<void>;
  total: number;
}

export const useAlerts = (
  skip: number = 0,
  limit: number = 100,
  severity?: string,
  isResolved?: boolean
): UseAlertsResult => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result: PaginatedResponse<Alert> = await getAlerts(skip, limit, severity, isResolved);
      setAlerts(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch alerts'));
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  }, [skip, limit, severity, isResolved]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleResolveAlert = useCallback(
    async (alertId: string) => {
      try {
        await apiResolveAlert(alertId);
        await fetchData();
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to resolve alert'));
      }
    },
    [fetchData]
  );

  return {
    alerts,
    loading,
    error,
    refetch: fetchData,
    resolveAlert: handleResolveAlert,
    total,
  };
};
