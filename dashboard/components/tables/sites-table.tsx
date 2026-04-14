import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Site } from '@/lib/types';
import { formatDate } from '@/lib/format';

interface SitesTableProps {
  sites: Site[];
}

export const SitesTable = ({ sites }: SitesTableProps) => {
  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Nom
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Ville
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Cameras
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Statut
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Cree le
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sites.map((site) => (
              <tr key={site.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <Link
                    href={`/sites/${site.id}`}
                    className="font-medium text-primary hover:text-primary-dark"
                  >
                    {site.name}
                  </Link>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{site.city}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{site.site_type}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{site.camera_count}</td>
                <td className="px-6 py-4">
                  <Badge variant={site.is_active ? 'success' : 'default'}>
                    {site.is_active ? 'Actif' : 'Inactif'}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {formatDate(site.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
