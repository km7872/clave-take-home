import { useState } from "react";
import { Send, Sparkles, X, Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { QueryVisualization } from "./QueryVisualization";

interface ChatInsightsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title?: string;
  insights?: string[];
}

interface Message {
  role: "assistant" | "user";
  content: string;
  data?: any;
  metadata?: {
    suggested_visualization?: string;
    x_axis?: string;
    y_axis?: string;
  };
}

export function ChatInsightsDialog({
  open,
  onOpenChange,
  title,
  insights,
}: ChatInsightsDialogProps) {
  const [messages, setMessages] = useState<Message[]>(() => {
    const initial: Message[] = [];
    if (title && insights && insights.length > 0) {
      initial.push({
        role: "assistant",
        content: `Here are the key insights for ${title}:\n\n${insights.map((i, idx) => `${idx + 1}. ${i}`).join("\n\n")}`,
      });
    } else {
      initial.push({
        role: "assistant",
        content: "Hi! I can help you analyze your restaurant data. Ask me anything like 'Show me top selling products' or 'What's the revenue by location?'",
      });
    }
    return initial;
  });
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    const queryText = input;
    setInput("");
    setIsLoading(true);

    try {
      // Use same port as other API calls - port 8001 based on chart components
      const apiBaseUrl = "http://127.0.0.1:8001";
      const response = await fetch(`${apiBaseUrl}/api/nlp-query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: queryText }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        let assistantContent = "";
        
        // Format response based on visualization type
        if (result.data && result.data.length > 0) {
          const vizType = result.metadata?.suggested_visualization || "table";
          
          if (vizType === "metric_card" && result.data.length === 1) {
            // Single metric value
            const value = Object.values(result.data[0])[1] || Object.values(result.data[0])[0];
            assistantContent = `The answer is: **${value}**\n\n*Visualization: ${vizType}*`;
          } else if (vizType === "text" || result.count === 0) {
            assistantContent = result.message || "No data found for your query.";
          } else {
            // Summarize data
            assistantContent = `Found ${result.count} result(s).\n\n*Visualization type: ${vizType}*\n`;
            if (result.summary) {
              assistantContent += `\nSummary:\n${JSON.stringify(result.summary, null, 2)}`;
            }
          }
        } else {
          assistantContent = result.message || "No data found for your query.";
        }

        const assistantMessage: Message = {
          role: "assistant",
          content: assistantContent,
          data: result.data,
          metadata: result.metadata,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage: Message = {
          role: "assistant",
          content: `Error: ${result.error || "Query failed. Please try rephrasing your question."}`,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        role: "assistant",
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}. Please try again.`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] w-full h-[95vh] bg-popover border-border p-0 gap-0 flex flex-col">
        <DialogHeader className="p-4 border-b border-border flex-shrink-0">
          <DialogTitle className="flex items-center gap-2 font-display text-lg">
            <Sparkles className="h-5 w-5 text-primary" />
            AI Analytics Chat
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-xl px-4 py-3 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                  }`}
                >
                  <p className="text-sm whitespace-pre-line">{message.content}</p>
                  {message.data && message.data.length > 0 && message.metadata && (
                    <div className="mt-4">
                      <QueryVisualization 
                        data={message.data} 
                        metadata={message.metadata}
                      />
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted text-foreground rounded-xl px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="p-4 border-t border-border flex-shrink-0">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-2"
          >
            <Input
              placeholder="Ask me anything about your restaurant data..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-muted border-border focus-visible:ring-primary"
              disabled={isLoading}
            />
            <Button 
              type="submit" 
              size="icon" 
              className="bg-primary hover:bg-primary/90"
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  );
}
