import { useState, useEffect } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { Loader2 } from "lucide-react";

const COLORS = [
  "hsl(var(--chart-3))",
  "hsl(var(--primary))",
  "hsl(var(--accent))",
];

const formatFulfillmentType = (type: string): string => {
  if (type === "DINE_IN") return "Dine-in";
  if (type === "PICKUP") return "Takeout";
  if (type === "DELIVERY") return "Delivery";
  return type.replace(/_/g, '-').toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase());
};

export function FulfillmentChart() {
  const [data, setData] = useState<Array<{ name: string; value: number }>>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const url = new URL('http://localhost:8001/api/orders/fulfillment-breakdown');
      url.searchParams.append('start_date', '2025-01-01T00:00:00Z');
      url.searchParams.append('end_date', '2025-01-04T23:59:59Z');

      console.log('Fetching fulfillment breakdown data:', {
        endpoint: '/api/orders/fulfillment-breakdown',
        startDate: '2025-01-01T00:00:00Z',
        endDate: '2025-01-04T23:59:59Z',
        url: url.toString()
      });

      try {
        const response = await fetch(url.toString());
        console.log('Fulfillment breakdown API response status:', response.status);

        const result = await response.json();
        console.log('Fulfillment breakdown API response data:', result);

        if (result.data && Array.isArray(result.data)) {
          const transformedData = result.data.map((item: any) => ({
            name: formatFulfillmentType(item.type || 'Unknown'),
            value: item.percentage || 0
          }));
          setData(transformedData);
        }
      } catch (error) {
        console.error('Error fetching fulfillment breakdown data:', error);
      } finally {
        setIsLoading(false);
        console.log('Fulfillment breakdown data fetch completed');
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[200px]">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={70}
          paddingAngle={4}
          dataKey="value"
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "white",
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
            color: "hsl(var(--foreground))",
          }}
          formatter={(value: number) => [`${value}%`, "Share"]}
        />
        <Legend
          verticalAlign="bottom"
          height={36}
          formatter={(value) => (
            <span style={{ color: "hsl(var(--foreground))", fontSize: "12px" }}>
              {value}
            </span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
