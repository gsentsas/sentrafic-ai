'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card } from '@/components/ui/card';

interface TrafficLineChartProps {
  data: Array<{
    timestamp: string;
    count?: number;
    [key: string]: string | number | undefined;
  }>;
  title: string;
  dataKey?: string;
}

export const TrafficLineChart = ({
  data,
  title,
  dataKey = 'count',
}: TrafficLineChartProps) => {
  return (
    <Card className="w-full">
      <h3 className="subsection-title">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="timestamp"
            stroke="#9ca3af"
            tick={{ fontSize: 12 }}
          />
          <YAxis stroke="#9ca3af" tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            }}
            cursor={{ stroke: '#2563eb', strokeWidth: 1 }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ fill: '#2563eb', r: 4 }}
            activeDot={{ r: 6 }}
            name="Vehicle Count"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};
