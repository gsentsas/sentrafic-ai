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
import { CLASS_COLORS } from '@/lib/constants';

interface DistributionPieChartProps {
  data: ClassDistribution[];
  title: string;
}

export const DistributionPieChart = ({ data, title }: DistributionPieChartProps) => {
  const chartData = data.map((item) => ({
    name: item.className,
    value: item.count,
    percentage: item.percentage,
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
            label={({ percentage }) => `${percentage.toFixed(1)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry) => (
              <Cell
                key={`cell-${entry.name}`}
                fill={(CLASS_COLORS as Record<string, string>)[entry.name.toLowerCase()] || '#9ca3af'}
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
            formatter={(value: number) => value.toLocaleString()}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
};
