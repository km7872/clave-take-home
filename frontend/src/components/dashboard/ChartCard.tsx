import { ReactNode, useState } from "react";
import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatInsightsDialog } from "./ChatInsightsDialog";

interface ChartCardProps {
  title: string;
  children: ReactNode;
  insights: string[];
  delay?: number;
  className?: string;
}

export function ChartCard({ title, children, insights, delay = 0, className = "" }: ChartCardProps) {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <>
      <div
        className={`glass-card p-6 opacity-0 animate-slide-up hover:border-primary/30 transition-all duration-300 group ${className}`}
        style={{ animationDelay: `${delay}ms`, animationFillMode: 'forwards' }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-foreground">{title}</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setChatOpen(true)}
            className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-primary hover:bg-primary/10"
          >
            <MessageCircle className="h-4 w-4 mr-1" />
            Chat
          </Button>
        </div>
        <div className="chart-container">{children}</div>
      </div>

      <ChatInsightsDialog
        open={chatOpen}
        onOpenChange={setChatOpen}
        title={title}
        insights={insights}
      />
    </>
  );
}
