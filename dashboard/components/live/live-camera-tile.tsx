import { Camera, Activity } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatCongestion } from '@/lib/format';
import { CAMERA_STATUS_COLORS, CONGESTION_COLORS } from '@/lib/constants';

interface LiveCameraTileProps {
  cameraName: string;
  siteName: string;
  status: 'online' | 'offline' | 'error';
  vehicleCount?: number;
  congestionLevel?: 'free' | 'moderate' | 'heavy' | 'blocked';
}

const statusVariants = {
  online: 'success',
  offline: 'default',
  error: 'danger',
} as const;

export const LiveCameraTile = ({
  cameraName,
  siteName,
  status,
  vehicleCount = 0,
  congestionLevel = 'free',
}: LiveCameraTileProps) => {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      {/* Video Placeholder */}
      <div className="relative bg-gray-900 aspect-video flex items-center justify-center">
        <Camera className="w-16 h-16 text-gray-600" />

        {/* Status Badge */}
        <div className="absolute top-3 right-3">
          <Badge variant={statusVariants[status]}>
            {status === 'online' && 'LIVE'}
            {status === 'offline' && 'OFFLINE'}
            {status === 'error' && 'ERROR'}
          </Badge>
        </div>

        {/* Congestion Indicator */}
        {status === 'online' && (
          <div
            className="absolute bottom-3 right-3 w-3 h-3 rounded-full animate-pulse"
            style={{ backgroundColor: CONGESTION_COLORS[congestionLevel] }}
          />
        )}
      </div>

      {/* Info Section */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 truncate">{cameraName}</h3>
        <p className="text-sm text-gray-600 truncate mb-3">{siteName}</p>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded-lg p-2">
            <p className="text-xs text-gray-600">Current Count</p>
            <p className="text-lg font-bold text-gray-900">{vehicleCount}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-2">
            <p className="text-xs text-gray-600">Congestion</p>
            <p
              className="text-sm font-bold"
              style={{ color: CONGESTION_COLORS[congestionLevel] }}
            >
              {formatCongestion(congestionLevel)}
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
};
