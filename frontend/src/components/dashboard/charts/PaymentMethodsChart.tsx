import { useState, useEffect } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { Loader2 } from "lucide-react";
import { useDateRange } from "@/contexts/DateRangeContext";
import { getApiUrl } from "@/config/api";

const COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--accent))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
];

const formatMethodName = (method: string): string => {
  if (method === "CARD") return "Card";
  if (method === "CASH") return "Cash";
  if (method === "MOBILE") return "Mobile";
  return method.charAt(0) + method.slice(1).toLowerCase();
};

export function PaymentMethodsChart() {
  const { dateRange } = useDateRange();
  const [data, setData] = useState<Array<{ name: string; value: number }>>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      const url = new URL(getApiUrl('/api/payments/method-breakdown'));
      url.searchParams.append('start_date', dateRange.startDate);
      url.searchParams.append('end_date', dateRange.endDate);

      console.log('Fetching payment methods data:', {
        endpoint: '/api/payments/method-breakdown',
        startDate: dateRange.startDate,
        endDate: dateRange.endDate,
        url: url.toString()
      });

      try {
        const response = await fetch(url.toString());
        console.log('Payment methods API response status:', response.status);

        const result = await response.json();
        console.log('Payment methods API response data:', result);

        if (result.data && Array.isArray(result.data)) {
          const transformedData = result.data.map((item: any) => ({
            name: formatMethodName(item.method || 'Unknown'),
            value: item.percentage || 0
          }));
          setData(transformedData);
        }
      } catch (error) {
        console.error('Error fetching payment methods data:', error);
      } finally {
        setIsLoading(false);
        console.log('Payment methods data fetch completed');
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
