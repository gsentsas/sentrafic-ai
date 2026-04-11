'use client';

import { useState, useEffect, useCallback } from 'react';
import { Camera, PaginatedResponse } from '@/lib/types';
import { getCameras } from '@/lib/api';

interface UseCamerasResult {
  cameras: Camera[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  total: number;
}

export const useCameras = (
  siteId?: string,
  skip: number = 0,
  limit: number = 100
): UseCamerasResult => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result: PaginatedResponse<Camera> = await getCameras(siteId, skip, limit);
      setCameras(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch cameras'));
      setCameras([]);
    } finally {
      setLoading(false);
    }
  }, [siteId, skip, limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    cameras,
    loading,
    error,
    refetch: fetchData,
    total,
  };
};
