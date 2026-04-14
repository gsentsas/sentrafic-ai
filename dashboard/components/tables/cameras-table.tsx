'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Camera } from '@/lib/types';
import { timeAgo } from '@/lib/format';
import { CAMERA_STATUS_LABELS } from '@/lib/constants';
import { updateCamera } from '@/lib/api';

interface CamerasTableProps {
  cameras: Camera[];
  onRefetch?: () => Promise<void>;
}

const statusVariants = {
  online: 'success',
  offline: 'default',
  error: 'danger',
} as const;

export const CamerasTable = ({ cameras, onRefetch }: CamerasTableProps) => {
  const router = useRouter();
  const [togglingId, setTogglingId] = useState<string | null>(null);

  const truncateUrl = (url: string) =>
    url.length > 38 ? url.substring(0, 38) + '…' : url;

  const handleToggleActive = async (
    e: React.MouseEvent,
    camera: Camera
  ) => {
    e.stopPropagation(); // ne pas naviguer vers le détail
    setTogglingId(camera.id);
    try {
      await updateCamera(camera.id, { is_active: !camera.is_active });
      await onRefetch?.();
    } catch {
      // silencieux — l'état ne change pas
    } finally {
      setTogglingId(null);
    }
  };

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Nom</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Site</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Statut</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Flux</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Emplacement</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Dernier signal</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Actif</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {cameras.map((camera) => (
              <tr
                key={camera.id}
                className={`hover:bg-gray-50 transition-colors cursor-pointer ${
                  !camera.is_active ? 'opacity-50' : ''
                }`}
                onClick={() => router.push(`/cameras/${camera.id}`)}
              >
                <td className="px-6 py-4 font-medium text-gray-900 hover:text-blue-600 transition-colors">
                  {camera.name}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{camera.site_name || '—'}</td>
                <td className="px-6 py-4">
                  <Badge variant={statusVariants[camera.status]}>
                    {CAMERA_STATUS_LABELS[camera.status] || camera.status}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 font-mono">
                  {truncateUrl(camera.stream_url)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {camera.location_description || '—'}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {camera.last_seen_at ? timeAgo(camera.last_seen_at) : 'Jamais'}
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={(e) => handleToggleActive(e, camera)}
                    disabled={togglingId === camera.id}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                      camera.is_active ? 'bg-green-500' : 'bg-gray-300'
                    } ${togglingId === camera.id ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                    title={camera.is_active ? 'Désactiver' : 'Activer'}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                        camera.is_active ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
