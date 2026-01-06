import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Loader2 } from "lucide-react";
import { useDateRange } from "@/contexts/DateRangeContext";

export function RevenueByLocationChart() {
  const { dateRange } = useDateRange();
  const [data, setData] = useState<Array<{ location: string; revenue: number }>>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const url = new URL('http://localhost:8001/api/metrics/revenue-by-location');
      url.searchParams.append('start_date', dateRange.startDate);
      url.searchParams.append('end_date', dateRange.endDate);

      console.log('Fetching revenue by location data:', {
        endpoint: '/api/metrics/revenue-by-location',
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        url: url.toString()
      });

      try {
        const response = await fetch(url.toString());
        console.log('Revenue by location API response status:', response.status);

        const result = await response.json();
        console.log('Revenue by location API response data:', result);

        if (result.data && Array.isArray(result.data)) {
          const transformedData = result.data.map((item: any) => ({
            location: item.location_name || item.location_id || 'Unknown',
            revenue: item.revenue || 0
          }));
          setData(transformedData);
        }
      } catch (error) {
        console.error('Error fetching revenue by location data:', error);
      } finally {
        setIsLoading(false);
        console.log('Revenue by location data fetch completed');
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
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
        <XAxis
          type="number"
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          // tickFormatter={(value) => `$${value / 1000}k`}
          tickFormatter={(value) => `$${value.toLocaleString()}`}
        />
        <YAxis
          type="category"
          dataKey="location"
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          width={80}
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
        <Bar
          dataKey="revenue"
          fill="hsl(var(--primary))"
          radius={[0, 4, 4, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
