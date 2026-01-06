/**
 * Reusable visualization components for query results.
 * Renders charts based on suggested_visualization type from API.
 */
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface QueryVisualizationProps {
  data: any[];
  metadata?: {
    suggested_visualization?: string;
    x_axis?: string;
    y_axis?: string;
  };
}

const COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--accent))",
  "#8884d8",
  "#82ca9d",
  "#ffc658",
  "#ff7300",
  "#00ff00",
];

export function QueryVisualization({ data, metadata }: QueryVisualizationProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-sm text-muted-foreground p-4 text-center">
        No data to visualize
      </div>
    );
  }

  const vizType = metadata?.suggested_visualization || "table";
  const xAxis = metadata?.x_axis;
  const yAxis = metadata?.y_axis;

  switch (vizType) {
    case "bar_chart":
      return <BarChartViz data={data} xAxis={xAxis} yAxis={yAxis} />;
    
    case "line_chart":
      return <LineChartViz data={data} xAxis={xAxis} yAxis={yAxis} />;
    
    case "pie_chart":
      return <PieChartViz data={data} xAxis={xAxis} yAxis={yAxis} />;
    
    case "metric_card":
      return <MetricCardViz data={data} />;
    
    case "table":
    default:
      return <TableViz data={data} />;
  }
}

function BarChartViz({ data, xAxis, yAxis }: { data: any[]; xAxis?: string; yAxis?: string }) {
  // Auto-detect axes if not provided
  const xKey = xAxis || Object.keys(data[0] || {})[0] || "name";
  const yKey = yAxis || Object.keys(data[0] || {}).find(
    key => typeof data[0]?.[key] === "number"
  ) || Object.keys(data[0] || {})[1] || "value";

  const chartData = data.map(item => ({
    [xKey]: item[xKey] || item[xKey.split(".").pop() || xKey] || "",
    [yKey]: typeof item[yKey] === "number" ? item[yKey] : 
            item[yKey.split(".").pop() || yKey] || 0,
  }));

  return (
    <div className="w-full h-[300px] mt-2">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
          <XAxis
            dataKey={xKey}
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            angle={xKey.length > 10 ? -20 : 0}
            textAnchor={xKey.length > 10 ? "end" : "middle"}
            height={xKey.length > 10 ? 60 : 30}
          />
          <YAxis
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => {
              if (yKey.toLowerCase().includes("revenue") || yKey.toLowerCase().includes("amount")) {
                return `$${value.toLocaleString()}`;
              }
              return value.toLocaleString();
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--popover))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              color: "hsl(var(--foreground))",
            }}
            formatter={(value: number) => {
              const formatted = yKey.toLowerCase().includes("revenue") || yKey.toLowerCase().includes("amount")
                ? `$${value.toLocaleString()}`
                : value.toLocaleString();
              return [formatted, yKey];
            }}
          />
          <Bar 
            dataKey={yKey} 
            fill="hsl(var(--primary))" 
            radius={[4, 4, 0, 0]} 
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function LineChartViz({ data, xAxis, yAxis }: { data: any[]; xAxis?: string; yAxis?: string }) {
  const xKey = xAxis || Object.keys(data[0] || {})[0] || "period";
  const yKey = yAxis || Object.keys(data[0] || {}).find(
    key => typeof data[0]?.[key] === "number"
  ) || Object.keys(data[0] || {})[1] || "value";

  const chartData = data.map(item => ({
    [xKey]: item[xKey] || item[xKey.split(".").pop() || xKey] || "",
    [yKey]: typeof item[yKey] === "number" ? item[yKey] : 
            item[yKey.split(".").pop() || yKey] || 0,
  }));

  return (
    <div className="w-full h-[300px] mt-2">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis
            dataKey={xKey}
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
            tickFormatter={(value) => {
              if (yKey.toLowerCase().includes("revenue") || yKey.toLowerCase().includes("amount")) {
                return `$${value / 1000}k`;
              }
              return value.toLocaleString();
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--popover))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              color: "hsl(var(--foreground))",
            }}
            formatter={(value: number) => {
              const formatted = yKey.toLowerCase().includes("revenue") || yKey.toLowerCase().includes("amount")
                ? `$${value.toLocaleString()}`
                : value.toLocaleString();
              return [formatted, yKey];
            }}
          />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke="hsl(var(--primary))"
            strokeWidth={3}
            dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, fill: "hsl(var(--primary))" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function PieChartViz({ data, xAxis, yAxis }: { data: any[]; xAxis?: string; yAxis?: string }) {
  const xKey = xAxis || Object.keys(data[0] || {})[1] || "name";
  const yKey = yAxis || Object.keys(data[0] || {}).find(
    key => typeof data[0]?.[key] === "number"
  ) || Object.keys(data[0] || {})[2] || "value";

  const chartData = data.map((item, idx) => ({
    name: item[xKey] || item[xKey.split(".").pop() || xKey] || `Item ${idx + 1}`,
    value: typeof item[yKey] === "number" ? item[yKey] : 
           item[yKey.split(".").pop() || yKey] || 0,
  }));

  return (
    <div className="w-full h-[300px] mt-2">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--popover))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              color: "hsl(var(--foreground))",
            }}
            formatter={(value: number) => value.toLocaleString()}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

function MetricCardViz({ data }: { data: any[] }) {
  const item = data[0] || {};
  // Find the first numeric value for display
  const valueKey = Object.keys(item).find(key => typeof item[key] === "number");
  const value = valueKey ? item[valueKey] : Object.values(item)[0];
  const label = valueKey || Object.keys(item)[0];

  return (
    <Card className="mt-2">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">
          {typeof value === "number" 
            ? (label?.toLowerCase().includes("revenue") || label?.toLowerCase().includes("amount")
                ? `$${value.toLocaleString()}`
                : value.toLocaleString())
            : String(value)}
        </div>
      </CardContent>
    </Card>
  );
}

function TableViz({ data }: { data: any[] }) {
  if (data.length === 0) return null;

  const columns = Object.keys(data[0]);

  return (
    <div className="mt-2 border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <TableHead key={col} className="font-semibold">
                {col.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.slice(0, 10).map((row, idx) => (
            <TableRow key={idx}>
              {columns.map((col) => (
                <TableCell key={col}>
                  {typeof row[col] === "number"
                    ? (col.toLowerCase().includes("revenue") || col.toLowerCase().includes("amount")
                        ? `$${row[col].toLocaleString()}`
                        : row[col].toLocaleString())
                    : String(row[col] || "")}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {data.length > 10 && (
        <div className="text-xs text-muted-foreground p-2 text-center">
          Showing 10 of {data.length} results
        </div>
      )}
    </div>
  );
}

