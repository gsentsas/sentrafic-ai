import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import LivePage from './page';
import { useLiveSummary } from '@/hooks/use-live-summary';

vi.mock('@/hooks/use-live-summary', () => ({
  useLiveSummary: vi.fn(),
}));

vi.mock('@/hooks/use-sites', () => ({
  useSites: () => ({
    sites: [],
    loading: false,
    error: null,
    refetch: vi.fn(async () => {}),
    total: 0,
  }),
}));

vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    React.createElement('a', { href }, children)
  ),
}));

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    replace: vi.fn(),
  }),
  usePathname: () => '/live',
  useSearchParams: () => ({
    get: () => null,
  }),
}));

Object.assign(globalThis, {
  navigator: {
    clipboard: {
      writeText: vi.fn(async () => {}),
    },
  },
});

vi.mock('@/components/layout/page-shell', () => ({
  PageShell: ({ children }: { children: React.ReactNode }) => React.createElement('div', null, children),
}));

vi.mock('@/components/ui/loading-state', () => ({
  LoadingState: ({ message }: { message?: string }) => React.createElement('div', null, message ?? 'loading'),
}));

vi.mock('@/components/ui/error-state', () => ({
  ErrorState: ({ message }: { message: string }) => React.createElement('div', null, message),
}));

vi.mock('@/components/ui/empty-state', () => ({
  EmptyState: ({ title }: { title: string }) => React.createElement('div', null, title),
}));

vi.mock('@/components/ui/modal', () => ({
  Modal: ({ isOpen, children }: { isOpen: boolean; children: React.ReactNode }) =>
    isOpen ? React.createElement('div', null, children) : null,
}));

vi.mock('@/components/live/live-camera-tile', () => ({
  LiveCameraTile: ({
    cameraName,
    cameraId,
    onToggleLive,
  }: {
    cameraName: string;
    cameraId: string;
    onToggleLive?: (cameraId: string) => void;
  }) =>
    React.createElement(
      'button',
      {
        type: 'button',
        onClick: () => onToggleLive?.(cameraId),
      },
      cameraName
    ),
}));

describe('LivePage', () => {
  it('renders priority error section and stale counter from live summary', () => {
    const refetch = vi.fn(async () => {});
    vi.mocked(useLiveSummary).mockReturnValue({
      loading: false,
      error: null,
      refetch,
      consecutiveFailures: 0,
      lastSuccessAt: new Date().toISOString(),
      pollingIntervalMs: 10_000,
      avgLatencyMs: 120,
      consecutiveSuccesses: 3,
      data: {
        timestamp: new Date().toISOString(),
        cameras: [
          {
            camera_id: 'cam-1',
            camera_name: 'Camera Erreur',
            site_name: 'Site A',
            status: 'error',
            stream_url: 'http://example.com/live.m3u8',
            last_seen_at: new Date().toISOString(),
            last_reading: null,
          },
          {
            camera_id: 'cam-2',
            camera_name: 'Camera Retard',
            site_name: 'Site B',
            status: 'online',
            stream_url: 'http://example.com/live2.m3u8',
            last_seen_at: new Date().toISOString(),
            last_reading: {
              total_count: 12,
              congestion_level: 'moderate',
              avg_occupancy: 0.3,
              timestamp: new Date(Date.now() - 120000).toISOString(),
              is_stale: true,
            },
          },
        ],
      },
    });

    render(React.createElement(LivePage));

    expect(screen.getByText(/Attention prioritaire/i)).toBeInTheDocument();
    expect(screen.getByText(/1 flux en retard/i)).toBeInTheDocument();
    expect(screen.getByText(/Camera Erreur/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Forcer synchro' }));
    expect(refetch).toHaveBeenCalled();
  });

  it('limits live wall selection to 4 cameras', () => {
    vi.mocked(useLiveSummary).mockReturnValue({
      loading: false,
      error: null,
      refetch: vi.fn(async () => {}),
      consecutiveFailures: 0,
      lastSuccessAt: new Date().toISOString(),
      pollingIntervalMs: 10_000,
      avgLatencyMs: 120,
      consecutiveSuccesses: 1,
      data: {
        timestamp: new Date().toISOString(),
        cameras: Array.from({ length: 5 }).map((_, idx) => ({
          camera_id: `cam-${idx + 1}`,
          camera_name: `Camera ${idx + 1}`,
          site_name: `Site ${idx + 1}`,
          status: 'online' as const,
          stream_url: `http://example.com/live-${idx + 1}.m3u8`,
          last_seen_at: new Date().toISOString(),
          last_reading: {
            total_count: 10 + idx,
            congestion_level: 'moderate',
            avg_occupancy: 0.2,
            timestamp: new Date().toISOString(),
            is_stale: false,
          },
        })),
      },
    });

    render(React.createElement(LivePage));

    fireEvent.click(screen.getByText('Camera 1'));
    fireEvent.click(screen.getByText('Camera 2'));
    fireEvent.click(screen.getByText('Camera 3'));
    fireEvent.click(screen.getByText('Camera 4'));
    fireEvent.click(screen.getByText('Camera 5'));

    expect(screen.getByText(/Mur live — 4\/4/i)).toBeInTheDocument();
  });

  it('applies preset "En retard" on stale online cameras', () => {
    vi.mocked(useLiveSummary).mockReturnValue({
      loading: false,
      error: null,
      refetch: vi.fn(async () => {}),
      consecutiveFailures: 0,
      lastSuccessAt: new Date().toISOString(),
      pollingIntervalMs: 10_000,
      avgLatencyMs: 120,
      consecutiveSuccesses: 1,
      data: {
        timestamp: new Date().toISOString(),
        cameras: [
          {
            camera_id: 'cam-stale',
            camera_name: 'Camera Stale',
            site_name: 'Site A',
            status: 'online',
            stream_url: 'http://example.com/stale.m3u8',
            last_seen_at: new Date().toISOString(),
            last_reading: {
              total_count: 10,
              congestion_level: 'moderate',
              avg_occupancy: 0.2,
              timestamp: new Date().toISOString(),
              is_stale: true,
            },
          },
          {
            camera_id: 'cam-fresh',
            camera_name: 'Camera Fresh',
            site_name: 'Site B',
            status: 'online',
            stream_url: 'http://example.com/fresh.m3u8',
            last_seen_at: new Date().toISOString(),
            last_reading: {
              total_count: 20,
              congestion_level: 'moderate',
              avg_occupancy: 0.3,
              timestamp: new Date().toISOString(),
              is_stale: false,
            },
          },
        ],
      },
    });

    render(React.createElement(LivePage));
    fireEvent.click(screen.getByRole('button', { name: 'En retard' }));

    expect(screen.getByText('Camera Stale')).toBeInTheDocument();
    expect(screen.queryByText('Camera Fresh')).not.toBeInTheDocument();
  });

  it('copies current view link', async () => {
    vi.mocked(useLiveSummary).mockReturnValue({
      loading: false,
      error: null,
      refetch: vi.fn(async () => {}),
      consecutiveFailures: 0,
      lastSuccessAt: new Date().toISOString(),
      pollingIntervalMs: 10_000,
      avgLatencyMs: 120,
      consecutiveSuccesses: 1,
      data: {
        timestamp: new Date().toISOString(),
        cameras: [],
      },
    });

    render(React.createElement(LivePage));
    fireEvent.click(screen.getByRole('button', { name: /Copier le lien de cette vue/i }));

    expect(navigator.clipboard.writeText).toHaveBeenCalled();
  });

  it('shows degraded API badge when polling fails repeatedly', () => {
    vi.mocked(useLiveSummary).mockReturnValue({
      loading: false,
      error: null,
      refetch: vi.fn(async () => {}),
      consecutiveFailures: 2,
      lastSuccessAt: null,
      pollingIntervalMs: 20_000,
      avgLatencyMs: null,
      consecutiveSuccesses: 0,
      data: {
        timestamp: new Date().toISOString(),
        cameras: [],
      },
    });

    render(React.createElement(LivePage));
    expect(screen.getByText(/API live DEGRADEE/i)).toBeInTheDocument();
    expect(screen.getByText(/Mode degrade active/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reessayer' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Ouvrir cameras' })).toBeInTheDocument();
  });

  it('hides live wall when degraded even if cameras are selected', () => {
    vi.mocked(useLiveSummary).mockReturnValue({
      loading: false,
      error: null,
      refetch: vi.fn(async () => {}),
      consecutiveFailures: 3,
      lastSuccessAt: new Date().toISOString(),
      pollingIntervalMs: 20_000,
      avgLatencyMs: 1500,
      consecutiveSuccesses: 0,
      data: {
        timestamp: new Date().toISOString(),
        cameras: [
          {
            camera_id: 'cam-1',
            camera_name: 'Camera 1',
            site_name: 'Site A',
            status: 'online',
            stream_url: 'http://example.com/live1.m3u8',
            last_seen_at: new Date().toISOString(),
            last_reading: {
              total_count: 15,
              congestion_level: 'moderate',
              avg_occupancy: 0.3,
              timestamp: new Date().toISOString(),
              is_stale: false,
            },
          },
        ],
      },
    });

    render(React.createElement(LivePage));
    fireEvent.click(screen.getByText('Camera 1'));

    expect(screen.queryByText(/Mur live —/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Mur live temporairement masque/i)).toBeInTheDocument();
  });

  it('shows latency level badge for high latency', () => {
    vi.mocked(useLiveSummary).mockReturnValue({
      loading: false,
      error: null,
      refetch: vi.fn(async () => {}),
      consecutiveFailures: 0,
      lastSuccessAt: new Date().toISOString(),
      pollingIntervalMs: 10_000,
      avgLatencyMs: 1300,
      consecutiveSuccesses: 1,
      data: {
        timestamp: new Date().toISOString(),
        cameras: [],
      },
    });

    render(React.createElement(LivePage));
    expect(screen.getByText(/Latence elevee/i)).toBeInTheDocument();
  });

  it('shows recovery message after stable successful polls', () => {
    vi.mocked(useLiveSummary).mockReturnValue({
      loading: false,
      error: null,
      refetch: vi.fn(async () => {}),
      consecutiveFailures: 0,
      lastSuccessAt: new Date().toISOString(),
      pollingIntervalMs: 10_000,
      avgLatencyMs: 220,
      consecutiveSuccesses: 4,
      data: {
        timestamp: new Date().toISOString(),
        cameras: [],
      },
    });

    render(React.createElement(LivePage));
    expect(screen.getByText(/Recuperation confirmee/i)).toBeInTheDocument();
  });
});
