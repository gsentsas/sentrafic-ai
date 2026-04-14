import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert } from '@/lib/types';
import { timeAgo } from '@/lib/format';
import { ALERT_TYPE_LABELS, ALERT_SEVERITY_LABELS } from '@/lib/constants';

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
                Severite
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
                Quand
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
                  alert.is_resolved ? 'bg-gray-50 opacity-60' : ''
                }`}
              >
                <td className="px-6 py-4">
                  <Badge variant={severityVariants[alert.severity]}>
                    {ALERT_SEVERITY_LABELS[alert.severity] || alert.severity}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {ALERT_TYPE_LABELS[alert.alert_type] || alert.alert_type}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {alert.short_description || alert.message}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{alert.camera_name || '—'}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{alert.site_name || '—'}</td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {timeAgo(alert.created_at)}
                </td>
                <td className="px-6 py-4">
                  {!alert.is_resolved && onResolve && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onResolve(alert.id)}
                      loading={resolvingId === alert.id}
                    >
                      Resoudre
                    </Button>
                  )}
                  {alert.is_resolved && (
                    <span className="text-xs text-gray-500 font-medium">Resolue</span>
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
