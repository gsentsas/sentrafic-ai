'use client';

import { useState, useEffect, useCallback } from 'react';
import { Site, PaginatedResponse } from '@/lib/types';
import { getSites } from '@/lib/api';

interface UseSitesResult {
  sites: Site[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  total: number;
  skip: number;
  limit: number;
}

export const useSites = (skip: number = 0, limit: number = 100): UseSitesResult => {
  const [sites, setSites] = useState<Site[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result: PaginatedResponse<Site> = await getSites(skip, limit);
      setSites(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch sites'));
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
    total,
    skip,
    limit,
  };
};
