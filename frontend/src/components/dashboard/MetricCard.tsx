import { ReactNode, useState, useEffect } from "react";
import { MessageCircle, TrendingUp, TrendingDown, Minus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatInsightsDialog } from "./ChatInsightsDialog";
import { useDateRange } from "@/contexts/DateRangeContext";
import { getApiUrl } from "@/config/api";

interface MetricCardProps {
  title: string;
  value?: string;
  change?: number;
  changeLabel?: string;
  icon: ReactNode;
  insights: string[];
  delay?: number;
  apiEndpoint?: string;
  startDate?: string;
  endDate?: string;
}

export function MetricCard({ 
  title, 
  value: valueProp, 
  change, 
  changeLabel = "vs last week",
  icon, 
  insights,
  delay = 0,
  apiEndpoint,
  startDate: startDateProp,
  endDate: endDateProp
}: MetricCardProps) {
  const { dateRange } = useDateRange();
  const [chatOpen, setChatOpen] = useState(false);
  const [value, setValue] = useState<string>(valueProp || "");
  const [isLoading, setIsLoading] = useState(false);

  // Use prop dates if provided, otherwise use context dates
  const startDate = startDateProp || dateRange.startDate;
  const endDate = endDateProp || dateRange.endDate;

  useEffect(() => {
    if (apiEndpoint && startDate && endDate) {
      const fetchData = async () => {
        setIsLoading(true);
        const url = new URL(getApiUrl(apiEndpoint));
        url.searchParams.append('start_date', startDate);
        url.searchParams.append('end_date', endDate);
        
        console.log('Fetching metric data:', {
          endpoint: apiEndpoint,
          startDate,
          endDate,
          url: url.toString()
        });

        try {
          const response = await fetch(url.toString());
          console.log('Metric API response status:', response.status);
          
          const data = await response.json();
          console.log('Metric API response data:', data);
          
          // Handle different response structures
          let numericValue: number | undefined;
          if (data.value !== undefined) {
            numericValue = data.value;
          } else if (data.data?.total_tips !== undefined) {
            numericValue = data.data.total_tips;
          } else if (data.summary?.overall_aov !== undefined) {
            numericValue = data.summary.overall_aov;
          }
          
          if (numericValue !== undefined) {
            const formattedValue = new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: 'USD',
              minimumFractionDigits: 0,
              maximumFractionDigits: 0,
            }).format(numericValue);
            setValue(formattedValue);
          }
        } catch (error) {
          console.error('Error fetching metric data:', error);
        } finally {
          setIsLoading(false);
          console.log('Metric data fetch completed');
        }
      };

      fetchData();
    } else if (valueProp) {
      setValue(valueProp);
    }
  }, [apiEndpoint, startDate, endDate, valueProp, dateRange]);

  const getTrendIcon = () => {
    if (change === undefined) return null;
    if (change > 0) return <TrendingUp className="h-4 w-4 text-success" />;
    if (change < 0) return <TrendingDown className="h-4 w-4 text-destructive" />;
    return <Minus className="h-4 w-4 text-muted-foreground" />;
  };

  const getTrendColor = () => {
    if (change === undefined) return "text-muted-foreground";
    if (change > 0) return "text-success";
    if (change < 0) return "text-destructive";
    return "text-muted-foreground";
  };

  return (
    <>
      <div 
        className="glass-card p-6 opacity-0 animate-slide-up hover:border-primary/30 transition-all duration-300 group"
        style={{ animationDelay: `${delay}ms`, animationFillMode: 'forwards' }}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="p-2 rounded-lg bg-primary/10 text-primary">
            {icon}
          </div>
          {/* <Button
            variant="ghost"
            size="sm"
            onClick={() => setChatOpen(true)}
            className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-primary hover:bg-primary/10"
          >
            <MessageCircle className="h-4 w-4 mr-1" />
            Chat
          </Button> */}
        </div>
        
        <p className="text-sm text-muted-foreground mb-1">{title}</p>
        {isLoading ? (
          <div className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            <p className="metric-value text-muted-foreground">Loading...</p>
          </div>
        ) : (
          <p className="metric-value text-foreground">{value}</p>
        )}
      </div>

      {/* <ChatInsightsDialog
        open={chatOpen}
        onOpenChange={setChatOpen}
        title={title}
        insights={insights}
      /> */}
    </>
  );
}
