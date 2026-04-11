import { AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { timeAgo } from '@/lib/format';
import { Alert } from '@/lib/types';
import { ALERT_SEVERITY_COLORS } from '@/lib/constants';

interface AlertCardProps extends Alert {
  onResolve?: () => void;
  isResolving?: boolean;
}

const severityVariants = {
  info: 'info',
  warning: 'warning',
  critical: 'danger',
} as const;

export const AlertCard = ({
  id,
  severity,
  alertType,
  message,
  cameraName,
  siteName,
  createdAt,
  isResolved,
  onResolve,
  isResolving = false,
}: AlertCardProps) => {
  return (
    <Card className="hover:shadow-md transition-shadow border-l-4" style={{
      borderLeftColor: ALERT_SEVERITY_COLORS[severity],
    }}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <div
            className="p-2 rounded-lg mt-1"
            style={{ backgroundColor: `${ALERT_SEVERITY_COLORS[severity]}20` }}
          >
            <AlertCircle
              className="w-5 h-5"
              style={{ color: ALERT_SEVERITY_COLORS[severity] }}
            />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h4 className="font-semibold text-gray-900">{alertType}</h4>
              <Badge variant={severityVariants[severity]}>{severity}</Badge>
            </div>
            <p className="text-sm text-gray-700 mb-2">{message}</p>
            <div className="flex gap-4 text-xs text-gray-600">
              <span>Camera: {cameraName}</span>
              <span>Site: {siteName}</span>
              <span>{timeAgo(createdAt)}</span>
            </div>
          </div>
        </div>
        {!isResolved && onResolve && (
          <Button
            variant="outline"
            size="sm"
            onClick={onResolve}
            loading={isResolving}
            className="ml-4"
          >
            Resolve
          </Button>
        )}
      </div>
    </Card>
  );
};
