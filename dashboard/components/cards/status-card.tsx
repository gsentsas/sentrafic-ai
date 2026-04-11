import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDateTime } from '@/lib/format';

interface StatusCardProps {
  title: string;
  status: 'online' | 'offline' | 'degraded';
  details: string;
  timestamp?: string;
}

const statusColors = {
  online: 'success',
  offline: 'default',
  degraded: 'warning',
} as const;

const statusText = {
  online: 'Online',
  offline: 'Offline',
  degraded: 'Degraded',
} as const;

export const StatusCard = ({
  title,
  status,
  details,
  timestamp,
}: StatusCardProps) => {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
          <p className="text-sm text-gray-600 mb-3">{details}</p>
          {timestamp && <p className="text-xs text-gray-500">{formatDateTime(timestamp)}</p>}
        </div>
        <Badge variant={statusColors[status]}>{statusText[status]}</Badge>
      </div>
    </Card>
  );
};
