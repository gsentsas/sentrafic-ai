import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert } from '@/lib/types';
import { timeAgo } from '@/lib/format';

interface AlertsTableProps {
  alerts: Alert[];
  onResolve?: (alertId: string) => Promise<void>;
  resolvingId?: string | null;
}

const severityVariants = {
  info: 'info',
  warning: 'warning',
  critical: 'danger',
} as const;

export const AlertsTable = ({ alerts, onResolve, resolvingId }: AlertsTableProps) => {
  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Message
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Camera
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Site
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <tr
                key={alert.id}
                className={`hover:bg-gray-50 transition-colors ${
                  alert.isResolved ? 'bg-gray-50 opacity-60' : ''
                }`}
              >
                <td className="px-6 py-4">
                  <Badge variant={severityVariants[alert.severity]}>
                    {alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {alert.alertType}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{alert.message}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{alert.cameraName}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{alert.siteName}</td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {timeAgo(alert.createdAt)}
                </td>
                <td className="px-6 py-4">
                  {!alert.isResolved && onResolve && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onResolve(alert.id)}
                      loading={resolvingId === alert.id}
                    >
                      Resolve
                    </Button>
                  )}
                  {alert.isResolved && (
                    <span className="text-xs text-gray-500 font-medium">Resolved</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
