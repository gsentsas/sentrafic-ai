'use client';

import { useState, useEffect, useCallback } from 'react';
import { DashboardOverview } from '@/lib/types';
import { getOverview } from '@/lib/api';
import { REFRESH_INTERVAL } from '@/lib/constants';

interface UseOverviewResult {
  data: DashboardOverview | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export const useOverview = (): UseOverviewResult => {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await getOverview();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch overview'));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
};
