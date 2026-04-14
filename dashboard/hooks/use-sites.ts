'use client';

import { useState, useEffect, useCallback } from 'react';
import { Site } from '@/lib/types';
import { getSites } from '@/lib/api';

interface UseSitesResult {
  sites: Site[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  total: number;
}

export const useSites = (skip: number = 0, limit: number = 100): UseSitesResult => {
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result: Site[] = await getSites(skip, limit);
      setSites(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Echec du chargement des sites'));
      setSites([]);
    } finally {
      setLoading(false);
    }
  }, [skip, limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    sites,
    loading,
    error,
    refetch: fetchData,
    total: sites.length,
  };
};
