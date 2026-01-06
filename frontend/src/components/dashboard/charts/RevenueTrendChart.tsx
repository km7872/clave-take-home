import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Loader2 } from "lucide-react";
import { useDateRange } from "@/contexts/DateRangeContext";

export function RevenueTrendChart() {
  const { dateRange } = useDateRange();
  const [data, setData] = useState<Array<{ period: string; revenue: number }>>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const url = new URL('http://localhost:8001/api/metrics/revenue-trend');
      url.searchParams.append('start_date', dateRange.startDate);
      url.searchParams.append('end_date', dateRange.endDate);
      url.searchParams.append('granularity', 'day');

      console.log('Fetching revenue trend data:', {
        endpoint: '/api/metrics/revenue-trend',
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        url: url.toString()
      });

      try {
        const response = await fetch(url.toString());
        console.log('Revenue trend API response status:', response.status);

        const result = await response.json();
        console.log('Revenue trend API response data:', result);

        if (result.data && Array.isArray(result.data)) {
          const transformedData = result.data.map((item: any) => ({
            period: item.period,
            revenue: item.revenue || 0
          }));
          setData(transformedData);
        }
      } catch (error) {
        console.error('Error fetching revenue trend data:', error);
      } finally {
        setIsLoading(false);
        console.log('Revenue trend data fetch completed');
      }
    };

    fetchData();
  }, [dateRange]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[250px]">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="period"
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `$${value / 1000}k`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--popover))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
            color: "hsl(var(--foreground))",
          }}
          formatter={(value: number) => [`$${value.toLocaleString()}`, "Revenue"]}
        />
        <Line
          type="monotone"
          dataKey="revenue"
          stroke="hsl(var(--primary))"
          strokeWidth={3}
          dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6, fill: "hsl(var(--primary))" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
