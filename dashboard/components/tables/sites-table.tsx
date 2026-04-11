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
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                City
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Cameras
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Created
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
                <td className="px-6 py-4 text-sm text-gray-600">{site.siteType}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{site.cameraCount}</td>
                <td className="px-6 py-4">
                  <Badge variant={site.isActive ? 'success' : 'default'}>
                    {site.isActive ? 'Active' : 'Inactive'}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {formatDate(site.createdAt)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
