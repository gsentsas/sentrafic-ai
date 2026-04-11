'use client';

import { useState, useEffect, useCallback } from 'react';
import { TrafficAggregate, ClassDistribution } from '@/lib/types';
import { getTrafficAnalytics, getClassDistribution } from '@/lib/api';

interface UseAnalyticsResult {
  data: TrafficAggregate[];
  distribution: ClassDistribution[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export const useAnalytics = (
  startDate: string,
  endDate: string,
  cameraId?: string,
  granularity: 'hour' | 'day' = 'hour'
): UseAnalyticsResult => {
  const [data, setData] = useState<TrafficAggregate[]>([]);
  const [distribution, setDistribution] = useState<ClassDistribution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [trafficData, distributionData] = await Promise.all([
        getTrafficAnalytics(startDate, endDate, cameraId, granularity),
        getClassDistribution(startDate, endDate, cameraId),
      ]);

      setData(trafficData);
      setDistribution(distributionData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch analytics'));
      setData([]);
      setDistribution([]);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, cameraId, granularity]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    distribution,
    loading,
    error,
    refetch: fetchData,
  };
};
