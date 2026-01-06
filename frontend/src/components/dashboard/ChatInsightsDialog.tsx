import { useState } from "react";
import { Send, Sparkles, X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ChatInsightsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  insights: string[];
}

interface Message {
  role: "assistant" | "user";
  content: string;
}

export function ChatInsightsDialog({
  open,
  onOpenChange,
  title,
  insights,
}: ChatInsightsDialogProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Here are the key insights for ${title}:\n\n${insights.map((i, idx) => `${idx + 1}. ${i}`).join("\n\n")}`,
    },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    
    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "Based on current trends, I recommend focusing on peak hour optimization to maximize revenue.",
        "The data suggests strong performance. Consider expanding promotional activities during slower periods.",
        "Customer behavior patterns indicate an opportunity for upselling during lunch hours.",
        "Comparing with industry benchmarks, your metrics are performing above average.",
      ];
      const response: Message = {
        role: "assistant",
        content: responses[Math.floor(Math.random() * responses.length)],
      };
      setMessages((prev) => [...prev, response]);
    }, 1000);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-popover border-border p-0 gap-0">
        <DialogHeader className="p-4 border-b border-border">
          <DialogTitle className="flex items-center gap-2 font-display text-lg">
            <Sparkles className="h-5 w-5 text-primary" />
            {title} Insights
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="h-[400px] p-4">
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
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        <div className="p-4 border-t border-border">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-2"
          >
            <Input
              placeholder="Ask about this metric..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-muted border-border focus-visible:ring-primary"
            />
            <Button type="submit" size="icon" className="bg-primary hover:bg-primary/90">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  );
}
