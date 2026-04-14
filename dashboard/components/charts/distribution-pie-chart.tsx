'use client';

import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Card } from '@/components/ui/card';
import { ClassDistribution } from '@/lib/types';
import { CLASS_COLORS, CLASS_LABELS } from '@/lib/constants';

interface DistributionPieChartProps {
  data: ClassDistribution[];
  title: string;
}

export const DistributionPieChart = ({ data, title }: DistributionPieChartProps) => {
  // Transform the backend ClassDistribution into chart-friendly format
  // Each ClassDistribution has a distribution record and total_count
  const mergedDistribution: Record<string, number> = {};
  let grandTotal = 0;

  data.forEach((item) => {
    Object.entries(item.distribution).forEach(([cls, count]) => {
      mergedDistribution[cls] = (mergedDistribution[cls] || 0) + count;
      grandTotal += count;
    });
  });

  const chartData = Object.entries(mergedDistribution).map(([cls, count]) => ({
    name: CLASS_LABELS[cls.toLowerCase()] || cls,
    classKey: cls.toLowerCase(),
    value: count,
    percentage: grandTotal > 0 ? (count / grandTotal) * 100 : 0,
  }));

  return (
    <Card className="w-full">
      <h3 className="subsection-title">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ percentage }: { percentage: number }) => `${percentage.toFixed(1)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry) => (
              <Cell
                key={`cell-${entry.name}`}
                fill={CLASS_COLORS[entry.classKey] || '#9ca3af'}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            }}
            formatter={(value: number) => value.toLocaleString('fr-FR')}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
};
