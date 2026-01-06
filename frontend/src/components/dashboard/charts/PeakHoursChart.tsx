import { useState, useEffect } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Loader2 } from "lucide-react";
import { useDateRange } from "@/contexts/DateRangeContext";
import { getApiUrl } from "@/config/api";

const formatHour = (hour: number): string => {
  if (hour === 0) return "12am";
  if (hour < 12) return `${hour}am`;
  if (hour === 12) return "12pm";
  return `${hour - 12}pm`;
};

export function PeakHoursChart() {
  const { dateRange } = useDateRange();
  const [data, setData] = useState<Array<{ hour: string; orders: number }>>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const url = new URL(getApiUrl('/api/time/peak-hours'));
      url.searchParams.append('start_date', dateRange.startDate);
      url.searchParams.append('end_date', dateRange.endDate);

      console.log('Fetching peak hours data:', {
        endpoint: '/api/time-analysis/peak-hours',
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        url: url.toString()
      });

      try {
        const response = await fetch(url.toString());
        console.log('Peak hours API response status:', response.status);

        const result = await response.json();
        console.log('Peak hours API response data:', result);

        if (result.data && Array.isArray(result.data)) {
          const transformedData = result.data
            .map((item: any) => ({
              hour: formatHour(item.hour),
              hourNum: item.hour,
              orders: item.order_count || 0
            }))
            .sort((a: any, b: any) => a.hourNum - b.hourNum)
            .map((item: any) => ({
              hour: item.hour,
              orders: item.orders
            }));
          setData(transformedData);
        }
      } catch (error) {
        console.error('Error fetching peak hours data:', error);
      } finally {
        setIsLoading(false);
        console.log('Peak hours data fetch completed');
      }
    };

    fetchData();
  }, [dateRange]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[200px]">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorOrders" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.4} />
            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="hour"
          stroke="hsl(var(--muted-foreground))"
          fontSize={11}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--popover))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
            color: "hsl(var(--foreground))",
          }}
          formatter={(value: number) => [value, "Orders"]}
        />
        <Area
          type="monotone"
          dataKey="orders"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorOrders)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
