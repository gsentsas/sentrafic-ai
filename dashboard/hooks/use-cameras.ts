'use client';

import { useState, useEffect, useCallback } from 'react';
import { Camera } from '@/lib/types';
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result: Camera[] = await getCameras(siteId, skip, limit);
      setCameras(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Echec du chargement des cameras'));
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
    total: cameras.length,
  };
};
