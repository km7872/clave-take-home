import { Utensils, Bell, Settings, Upload, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export function DashboardHeader() {
  return (
    <header className="flex items-center justify-between mb-8 opacity-0 animate-fade-in" style={{ animationFillMode: 'forwards' }}>
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-primary/20 text-primary">
          <Utensils className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-foreground">Bridger Inc</h1>
          <p className="text-sm text-muted-foreground">Real-time analytics for restaurants</p>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <Button variant="outline" size="lg" className="flex items-center">
          <MessageCircle className="h-5 w-5 mr-2" />
          Chat
        </Button>

      <Button variant="outline" size="lg" className="flex items-center">
        <Upload className="h-5 w-5 mr-2" />
        Import Data
      </Button>
      </div>
      </header>
  );
}
