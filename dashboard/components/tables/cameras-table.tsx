import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Camera } from '@/lib/types';
import { timeAgo } from '@/lib/format';
import { CAMERA_STATUS_COLORS } from '@/lib/constants';

interface CamerasTableProps {
  cameras: Camera[];
}

const statusVariants = {
  online: 'success',
  offline: 'default',
  error: 'danger',
} as const;

export const CamerasTable = ({ cameras }: CamerasTableProps) => {
  const truncateUrl = (url: string) => {
    return url.length > 40 ? url.substring(0, 40) + '...' : url;
  };

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Camera Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Site
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Stream URL
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Last Seen
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {cameras.map((camera) => (
              <tr key={camera.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 font-medium text-gray-900">{camera.name}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{camera.siteName}</td>
                <td className="px-6 py-4">
                  <Badge variant={statusVariants[camera.status]}>
                    {camera.status.charAt(0).toUpperCase() + camera.status.slice(1)}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 font-mono">
                  {truncateUrl(camera.streamUrl)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {camera.locationDescription}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {timeAgo(camera.createdAt)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
