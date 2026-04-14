'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { getLiveSummary } from '@/lib/api';
import { LiveSummaryResponse } from '@/lib/types';

interface UseLiveSummaryResult {
  data: LiveSummaryResponse | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  consecutiveFailures: number;
  lastSuccessAt: string | null;
  pollingIntervalMs: number;
  avgLatencyMs: number | null;
  consecutiveSuccesses: number;
}

interface LiveSummaryFilters {
  siteId?: string;
  status?: 'online' | 'offline' | 'error' | '';
}

export const useLiveSummary = (filters?: LiveSummaryFilters): UseLiveSummaryResult => {
  const [data, setData] = useState<LiveSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [consecutiveFailures, setConsecutiveFailures] = useState(0);
  const [consecutiveSuccesses, setConsecutiveSuccesses] = useState(0);
  const [lastSuccessAt, setLastSuccessAt] = useState<string | null>(null);
  const [latencySamples, setLatencySamples] = useState<number[]>([]);
  const previousHealthRef = useRef<'ok' | 'degraded' | null>(null);
  const pollingIntervalMs = consecutiveFailures >= 2 ? 20_000 : 10_000;
  const avgLatencyMs = latencySamples.length
    ? Math.round(latencySamples.reduce((sum, value) => sum + value, 0) / latencySamples.length)
    : null;
  const healthState: 'ok' | 'degraded' = consecutiveFailures >= 2 ? 'degraded' : 'ok';

  const fetchData = useCallback(async () => {
    const startedAt = Date.now();
    try {
      setError(null);
      const result = await getLiveSummary(filters);
      setData(result);
      setConsecutiveFailures(0);
      setConsecutiveSuccesses((prev) => prev + 1);
      setLastSuccessAt(new Date().toISOString());
      const elapsed = Date.now() - startedAt;
      setLatencySamples((prev) => [...prev.slice(-4), elapsed]);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Echec du chargement live'));
      setConsecutiveFailures((prev) => prev + 1);
      setConsecutiveSuccesses(0);
    } finally {
      setLoading(false);
    }
  }, [filters?.siteId, filters?.status]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, pollingIntervalMs);
    return () => clearInterval(interval);
  }, [fetchData, pollingIntervalMs]);

  useEffect(() => {
    const previous = previousHealthRef.current;
    if (previous && previous !== healthState) {
      console.info(`[live-summary] health transition: ${previous} -> ${healthState}`);
    }
    previousHealthRef.current = healthState;
  }, [healthState]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    consecutiveFailures,
    lastSuccessAt,
    pollingIntervalMs,
    avgLatencyMs,
    consecutiveSuccesses,
  };
};
