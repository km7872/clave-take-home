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

export function TopSellingChart() {
  const [data, setData] = useState<Array<{ product: string; sales: number }>>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const url = new URL('http://localhost:8001/api/products/top-selling');
      url.searchParams.append('start_date', '2025-01-01T00:00:00Z');
      url.searchParams.append('end_date', '2025-01-04T23:59:59Z');
      url.searchParams.append('limit', '5');
      url.searchParams.append('metric', 'quantity');

      console.log('Fetching top selling products data:', {
        endpoint: '/api/products/top-selling',
        startDate: '2025-01-01T00:00:00Z',
        endDate: '2025-01-04T23:59:59Z',
        url: url.toString()
      });

      try {
        const response = await fetch(url.toString());
        console.log('Top selling products API response status:', response.status);

        const result = await response.json();
        console.log('Top selling products API response data:', result);

        if (result.data && Array.isArray(result.data)) {
          const transformedData = result.data.map((item: any) => ({
            product: item.name || item.item_name || 'Unknown',
            sales: item.quantity || 0
          }));
          setData(transformedData);
        }
      } catch (error) {
        console.error('Error fetching top selling products data:', error);
      } finally {
        setIsLoading(false);
        console.log('Top selling products data fetch completed');
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[250px]">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
        <XAxis
          dataKey="product"
          stroke="hsl(var(--muted-foreground))"
          fontSize={11}
          tickLine={false}
          axisLine={false}
          angle={-20}
          textAnchor="end"
          height={60}
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
          formatter={(value: number) => [value.toLocaleString(), "Units Sold"]}
        />
        <Bar dataKey="sales" fill="hsl(var(--accent))" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
