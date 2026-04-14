'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { PageShell } from '@/components/layout/page-shell';
import { LoadingState } from '@/components/ui/loading-state';
import { ErrorState } from '@/components/ui/error-state';
import { EmptyState } from '@/components/ui/empty-state';
import { Modal } from '@/components/ui/modal';
import { LiveCameraTile } from '@/components/live/live-camera-tile';
import { useLiveSummary } from '@/hooks/use-live-summary';
import { useSites } from '@/hooks/use-sites';
import { Radio, Wifi, WifiOff, AlertCircle, Maximize2, Link as LinkIcon, Check } from 'lucide-react';

export default function LivePage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [initializedFromUrl, setInitializedFromUrl] = useState(false);
  const [selectedSiteId, setSelectedSiteId] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<'' | 'online' | 'offline' | 'error'>('');
  const [preset, setPreset] = useState<'' | 'errors' | 'stale' | 'online'>('');
  const [copied, setCopied] = useState(false);
  const [manualRefreshInProgress, setManualRefreshInProgress] = useState(false);
  const [nowMs, setNowMs] = useState(Date.now());
  const { sites } = useSites();
  const {
    data,
    loading,
    error,
    refetch,
    consecutiveFailures,
    lastSuccessAt,
    pollingIntervalMs,
    avgLatencyMs,
    consecutiveSuccesses,
  } = useLiveSummary({
    siteId: selectedSiteId || undefined,
    status: selectedStatus,
  });
  const cameras = (data?.cameras ?? []).map((camera) => ({
    id: camera.camera_id,
    site_id: '',
    site_name: camera.site_name,
    name: camera.camera_name,
    stream_url: camera.stream_url,
    status: camera.status,
    location_description: '',
    is_active: true,
    last_seen_at: camera.last_seen_at,
    health_label: 'unknown' as const,
    created_at: '',
    last_reading: camera.last_reading,
  }));
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null);
  const [liveWallCameraIds, setLiveWallCameraIds] = useState<string[]>([]);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const selectedCamera = useMemo(
    () => cameras.find((camera) => camera.id === selectedCameraId) ?? null,
    [cameras, selectedCameraId]
  );

  const streamUrl = selectedCamera?.stream_url ?? '';
  const isBrowserPlayable =
    !!streamUrl &&
    !streamUrl.startsWith('rtsp://') &&
    !streamUrl.startsWith('rtsp+tcp://');

  const handleFullscreen = () => {
    const video = videoRef.current;
    if (!video) return;

    if (video.requestFullscreen) {
      void video.requestFullscreen();
      return;
    }

    const webkitVideo = video as HTMLVideoElement & {
      webkitEnterFullscreen?: () => void;
    };
    if (webkitVideo.webkitEnterFullscreen) {
      webkitVideo.webkitEnterFullscreen();
    }
  };

  const toggleLiveWallCamera = (cameraId: string) => {
    setLiveWallCameraIds((prev) => {
      if (prev.includes(cameraId)) return prev.filter((id) => id !== cameraId);
      if (prev.length >= 4) return prev;
      return [...prev, cameraId];
    });
  };

  const handleCopyViewLink = async () => {
    const url = typeof window !== 'undefined' ? window.location.href : '';
    if (!url) return;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  };

  const handleManualRefresh = async () => {
    setManualRefreshInProgress(true);
    try {
      await refetch();
    } finally {
      setManualRefreshInProgress(false);
    }
  };

  useEffect(() => {
    const timer = setInterval(() => setNowMs(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (initializedFromUrl) return;
    const siteFromUrl = searchParams.get('site') ?? '';
    const statusFromUrl = searchParams.get('status');
    const presetFromUrl = searchParams.get('preset');
    if (siteFromUrl) setSelectedSiteId(siteFromUrl);
    if (statusFromUrl === 'online' || statusFromUrl === 'offline' || statusFromUrl === 'error') {
      setSelectedStatus(statusFromUrl);
    }
    if (presetFromUrl === 'errors' || presetFromUrl === 'stale' || presetFromUrl === 'online') {
      setPreset(presetFromUrl);
    }
    setInitializedFromUrl(true);
  }, [initializedFromUrl, searchParams]);

  useEffect(() => {
    if (!initializedFromUrl) return;
    const params = new URLSearchParams();
    if (selectedSiteId) params.set('site', selectedSiteId);
    if (selectedStatus) params.set('status', selectedStatus);
    if (preset) params.set('preset', preset);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }, [initializedFromUrl, pathname, preset, router, selectedSiteId, selectedStatus]);

  if (loading) {
    return (
      <PageShell title="Supervision live">
        <LoadingState message="Chargement des caméras..." />
      </PageShell>
    );
  }

  if (error) {
    return (
      <PageShell title="Supervision live">
        <ErrorState
          message="Impossible de charger la liste des caméras. Vérifiez votre connexion au backend."
          onRetry={refetch}
        />
      </PageShell>
    );
  }

  const filteredByPreset = preset === 'stale'
    ? cameras.filter((c) => c.status === 'online' && c.last_reading?.is_stale)
    : cameras;
  const onlineCameras = filteredByPreset.filter((c) => c.status === 'online');
  const offlineCameras = filteredByPreset.filter((c) => c.status === 'offline');
  const errorCameras = filteredByPreset.filter((c) => c.status === 'error');
  const staleOnlineCameras = onlineCameras.filter((camera) => camera.last_reading?.is_stale);
  const liveWallCameras = liveWallCameraIds
    .map((id) => filteredByPreset.find((camera) => camera.id === id))
    .filter((camera): camera is NonNullable<typeof camera> => !!camera);
  const liveApiHealth: 'ok' | 'degraded' = consecutiveFailures >= 2 ? 'degraded' : 'ok';
  const shouldShowLiveWall = liveWallCameras.length > 0 && liveApiHealth === 'ok';
  const latencyLevel: 'good' | 'warn' | 'bad' | 'unknown' =
    avgLatencyMs === null
      ? 'unknown'
      : avgLatencyMs < 400
        ? 'good'
        : avgLatencyMs < 1000
          ? 'warn'
          : 'bad';
  const latencyBadgeClass =
    latencyLevel === 'good'
      ? 'bg-green-50 text-green-700'
      : latencyLevel === 'warn'
        ? 'bg-amber-50 text-amber-700'
        : latencyLevel === 'bad'
          ? 'bg-red-50 text-red-700'
          : 'bg-gray-100 text-gray-600';
  const latencyLabel =
    latencyLevel === 'good'
      ? 'Latence OK'
      : latencyLevel === 'warn'
        ? 'Latence moyenne'
        : latencyLevel === 'bad'
          ? 'Latence elevee'
          : 'Latence indisponible';
  const lastSuccessAgo = (() => {
    if (!lastSuccessAt) return null;
    const diffSec = Math.max(0, Math.round((nowMs - new Date(lastSuccessAt).getTime()) / 1000));
    if (diffSec < 60) return `il y a ${diffSec}s`;
    const min = Math.floor(diffSec / 60);
    const sec = diffSec % 60;
    return `il y a ${min}m ${sec}s`;
  })();

  return (
    <PageShell title="Supervision live">
      {/* En-tête */}
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-6 mb-2">
          <h2 className="text-xl font-semibold text-gray-900">
            Supervision en temps réel
          </h2>
          <div
            className={`inline-flex items-center gap-1.5 text-xs font-medium rounded-full px-2.5 py-1 ${
              liveApiHealth === 'ok'
                ? 'bg-green-50 text-green-700'
                : 'bg-amber-50 text-amber-700'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                liveApiHealth === 'ok' ? 'bg-green-500' : 'bg-amber-500'
              }`}
            />
            API live {liveApiHealth === 'ok' ? 'OK' : 'DEGRADEE'}
          </div>
          <div className="flex items-center gap-1.5 text-sm text-gray-500">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Mise à jour toutes les {Math.round(pollingIntervalMs / 1000)} s
          </div>
          <button
            type="button"
            onClick={handleManualRefresh}
            disabled={manualRefreshInProgress}
            className="inline-flex items-center gap-1.5 text-xs font-medium rounded-md border border-gray-200 bg-white px-2.5 py-1.5 text-gray-700 hover:bg-gray-50 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {manualRefreshInProgress ? 'Synchro...' : 'Forcer synchro'}
          </button>
        </div>
        {lastSuccessAt && lastSuccessAgo && (
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <p className="text-xs text-gray-400">
              Derniere synchro API: {lastSuccessAgo}
              {avgLatencyMs !== null ? ` · latence moyenne ${avgLatencyMs} ms` : ''}
            </p>
            <span className={`text-[11px] font-medium rounded-full px-2 py-0.5 ${latencyBadgeClass}`}>
              {latencyLabel}
            </span>
          </div>
        )}
        <p className="text-gray-500 mb-5">
          Vue d'ensemble de toutes les caméras actives et de leur trafic en cours
        </p>
        <p className="text-sm text-blue-600 mb-5">
          Clique sur une tuile pour l'ajouter au mur live (max 4).
        </p>

        <div className="mb-4">
          <button
            type="button"
            onClick={handleCopyViewLink}
            className="inline-flex items-center gap-2 rounded-md border border-gray-200 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-green-600" /> : <LinkIcon className="w-3.5 h-3.5" />}
            {copied ? 'Lien copié' : 'Copier le lien de cette vue'}
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          <button
            type="button"
            onClick={() => {
              setPreset('');
              setSelectedStatus('');
            }}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
              preset === '' ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-white border-gray-200 text-gray-600'
            }`}
          >
            Tout
          </button>
          <button
            type="button"
            onClick={() => {
              setPreset('errors');
              setSelectedStatus('error');
            }}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
              preset === 'errors' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-white border-gray-200 text-gray-600'
            }`}
          >
            Erreurs
          </button>
          <button
            type="button"
            onClick={() => {
              setPreset('stale');
              setSelectedStatus('online');
            }}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
              preset === 'stale' ? 'bg-amber-50 border-amber-200 text-amber-700' : 'bg-white border-gray-200 text-gray-600'
            }`}
          >
            En retard
          </button>
          <button
            type="button"
            onClick={() => {
              setPreset('online');
              setSelectedStatus('online');
            }}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
              preset === 'online' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-white border-gray-200 text-gray-600'
            }`}
          >
            En ligne
          </button>
        </div>

        <div className="flex flex-wrap gap-3 mb-5">
          <select
            value={selectedSiteId}
            onChange={(e) => {
              setSelectedSiteId(e.target.value);
              setPreset('');
            }}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm bg-white"
          >
            <option value="">Tous les sites</option>
            {sites.map((site) => (
              <option key={site.id} value={site.id}>
                {site.name}
              </option>
            ))}
          </select>
          <select
            value={selectedStatus}
            onChange={(e) => {
              setSelectedStatus(e.target.value as '' | 'online' | 'offline' | 'error');
              setPreset('');
            }}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm bg-white"
          >
            <option value="">Tous les statuts</option>
            <option value="online">En ligne</option>
            <option value="offline">Hors ligne</option>
            <option value="error">Erreur</option>
          </select>
        </div>

        {/* Compteurs statut */}
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2 bg-green-50 text-green-700 px-4 py-2 rounded-xl text-sm font-medium">
            <Wifi className="w-4 h-4" />
            {onlineCameras.length} en ligne
          </div>
          {offlineCameras.length > 0 && (
            <div className="flex items-center gap-2 bg-gray-100 text-gray-600 px-4 py-2 rounded-xl text-sm font-medium">
              <WifiOff className="w-4 h-4" />
              {offlineCameras.length} hors ligne
            </div>
          )}
          {errorCameras.length > 0 && (
            <div className="flex items-center gap-2 bg-red-50 text-red-600 px-4 py-2 rounded-xl text-sm font-medium">
              <AlertCircle className="w-4 h-4" />
              {errorCameras.length} en erreur
            </div>
          )}
          {staleOnlineCameras.length > 0 && (
            <div className="flex items-center gap-2 bg-amber-50 text-amber-700 px-4 py-2 rounded-xl text-sm font-medium">
              <AlertCircle className="w-4 h-4" />
              {staleOnlineCameras.length} flux en retard
            </div>
          )}
        </div>
      </div>

      {liveApiHealth === 'degraded' && (
        <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-amber-800">Mode degrade active</p>
              <p className="text-xs text-amber-700 mt-1">
                Le flux live rencontre des erreurs repetees. Verifie le backend, la connectivite reseau et l'etat des cameras.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleManualRefresh}
                disabled={manualRefreshInProgress}
                className="inline-flex items-center gap-1.5 rounded-md border border-amber-300 bg-white px-2.5 py-1.5 text-xs font-medium text-amber-800 hover:bg-amber-100 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {manualRefreshInProgress ? 'Synchro...' : 'Reessayer'}
              </button>
              <Link
                href="/cameras"
                className="inline-flex items-center gap-1.5 rounded-md border border-amber-300 bg-white px-2.5 py-1.5 text-xs font-medium text-amber-800 hover:bg-amber-100"
              >
                Ouvrir cameras
              </Link>
            </div>
          </div>
        </div>
      )}

      {liveApiHealth === 'ok' && consecutiveSuccesses >= 3 && (
        <div className="mb-6 rounded-xl border border-green-200 bg-green-50 p-3">
          <p className="text-xs font-medium text-green-800">
            Recuperation confirmee: mode normal restaure ({consecutiveSuccesses} succes consecutifs).
          </p>
        </div>
      )}

      {shouldShowLiveWall && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
              Mur live — {liveWallCameras.length}/4
            </h3>
            <button
              type="button"
              onClick={() => setLiveWallCameraIds([])}
              className="text-xs font-medium text-gray-500 hover:text-gray-700"
            >
              Réinitialiser
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {liveWallCameras.map((camera) => {
              const playable =
                camera.stream_url &&
                !camera.stream_url.startsWith('rtsp://') &&
                !camera.stream_url.startsWith('rtsp+tcp://');
              return (
                <button
                  key={camera.id}
                  type="button"
                  onClick={() => setSelectedCameraId(camera.id)}
                  className="text-left rounded-xl border border-gray-200 overflow-hidden bg-white hover:shadow-md transition-shadow"
                >
                  <div className="relative aspect-video bg-black">
                    {playable ? (
                      <video
                        src={camera.stream_url}
                        muted
                        autoPlay
                        playsInline
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center px-4 text-center text-xs text-white/70">
                        Flux RTSP non lisible dans le navigateur.
                      </div>
                    )}
                  </div>
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium text-gray-900 truncate">{camera.name}</p>
                    <p className="text-xs text-gray-500 truncate">{camera.site_name ?? 'Site inconnu'}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {liveApiHealth === 'degraded' && liveWallCameraIds.length > 0 && (
        <div className="mb-8 rounded-xl border border-gray-200 bg-gray-50 p-4">
          <p className="text-sm font-medium text-gray-700">
            Mur live temporairement masque en mode degrade pour eviter des flux obsoletes.
          </p>
        </div>
      )}

      {errorCameras.length > 0 && (
        <div className="mb-8">
          <h3 className="text-sm font-semibold text-red-600 uppercase tracking-wider mb-4">
            Attention prioritaire — caméras en erreur ({errorCameras.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {errorCameras.map((camera) => (
              <LiveCameraTile
                key={`priority-${camera.id}`}
                cameraId={camera.id}
                cameraName={camera.name}
                siteName={camera.site_name}
                streamUrl={camera.stream_url}
                status={camera.status}
                lastSeenAt={camera.last_seen_at}
                selected={liveWallCameraIds.includes(camera.id)}
                onToggleLive={toggleLiveWallCamera}
                trafficSnapshot={camera.last_reading}
              />
            ))}
          </div>
        </div>
      )}

      {cameras.length === 0 ? (
        <EmptyState
          icon={Radio}
          title="Aucune caméra configurée"
          description="Ajoutez des caméras depuis la page Caméras pour démarrer la supervision."
          actionLabel="Gérer les caméras"
        />
      ) : (
        <>
          {onlineCameras.length > 0 && (
            <div className="mb-8">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
                Caméras actives — {onlineCameras.length}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {onlineCameras.map((camera) => (
                  <LiveCameraTile
                    key={camera.id}
                    cameraId={camera.id}
                    cameraName={camera.name}
                    siteName={camera.site_name}
                    streamUrl={camera.stream_url}
                    status={camera.status}
                    lastSeenAt={camera.last_seen_at}
                    selected={liveWallCameraIds.includes(camera.id)}
                    onToggleLive={toggleLiveWallCamera}
                    trafficSnapshot={camera.last_reading}
                  />
                ))}
              </div>
            </div>
          )}

          {offlineCameras.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
                Caméras hors ligne — {offlineCameras.length}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {offlineCameras.map((camera) => (
                  <LiveCameraTile
                    key={camera.id}
                    cameraId={camera.id}
                    cameraName={camera.name}
                    siteName={camera.site_name}
                    streamUrl={camera.stream_url}
                    status={camera.status}
                    lastSeenAt={camera.last_seen_at}
                    selected={liveWallCameraIds.includes(camera.id)}
                    onToggleLive={toggleLiveWallCamera}
                    trafficSnapshot={camera.last_reading}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}

      <Modal
        isOpen={!!selectedCamera}
        onClose={() => setSelectedCameraId(null)}
        title={selectedCamera ? `Live - ${selectedCamera.name}` : 'Live'}
        maxWidth="lg"
      >
        {selectedCamera && (
          <div className="space-y-4">
            <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
              {isBrowserPlayable ? (
                <>
                  <video
                    ref={videoRef}
                    key={streamUrl}
                    src={streamUrl}
                    controls
                    autoPlay
                    muted
                    playsInline
                    className="w-full h-full object-cover"
                  />
                  <button
                    type="button"
                    onClick={handleFullscreen}
                    className="absolute top-3 right-3 inline-flex items-center gap-1.5 rounded-md bg-black/60 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-black/75"
                  >
                    <Maximize2 className="w-3.5 h-3.5" />
                    Plein écran
                  </button>
                </>
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-center px-6">
                  <p className="text-sm text-white/90 mb-2">
                    Ce flux n'est pas lisible directement dans le navigateur.
                  </p>
                  <p className="text-xs text-white/60 break-all">{streamUrl || 'Aucun flux'}</p>
                </div>
              )}
            </div>

            <div className="flex items-center justify-between gap-3">
              <p className="text-sm text-gray-500 truncate">
                {selectedCamera.site_name ?? 'Site inconnu'}
              </p>
              <Link
                href={`/cameras/${selectedCamera.id}`}
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
              >
                Ouvrir la page caméra
              </Link>
            </div>
          </div>
        )}
      </Modal>
    </PageShell>
  );
}
