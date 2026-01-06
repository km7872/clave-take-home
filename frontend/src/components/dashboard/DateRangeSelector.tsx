import { useState, useEffect } from "react";
import { CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useDateRange } from "@/contexts/DateRangeContext";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

type DatePreset = "day" | "week" | "month" | "custom";

export function DateRangeSelector() {
  const { dateRange, setDateRange } = useDateRange();
  const [preset, setPreset] = useState<DatePreset>("custom");
  const [startDate, setStartDate] = useState<Date | undefined>(
    new Date(dateRange.startDate)
  );
  const [endDate, setEndDate] = useState<Date | undefined>(
    new Date(dateRange.endDate)
  );
  const [isOpen, setIsOpen] = useState(false);

  // Sync local state with context when context changes
  useEffect(() => {
    setStartDate(new Date(dateRange.startDate));
    setEndDate(new Date(dateRange.endDate));
  }, [dateRange]);

  const applyDateRange = (start: Date, end: Date) => {
    const startISO = new Date(start);
    startISO.setHours(0, 0, 0, 0);
    
    const endISO = new Date(end);
    endISO.setHours(23, 59, 59, 999);

    setDateRange({
      startDate: startISO.toISOString(),
      endDate: endISO.toISOString(),
    });
    setStartDate(start);
    setEndDate(end);
  };

  const handlePresetChange = (value: DatePreset) => {
    setPreset(value);
    const now = new Date();
    let start: Date;
    let end: Date = new Date(now);
    end.setHours(23, 59, 59, 999);

    switch (value) {
      case "day":
        start = new Date(now);
        start.setHours(0, 0, 0, 0);
        break;
      case "week":
        start = new Date(now);
        start.setDate(now.getDate() - 7);
        start.setHours(0, 0, 0, 0);
        break;
      case "month":
        start = new Date(now);
        start.setMonth(now.getMonth() - 1);
        start.setHours(0, 0, 0, 0);
        break;
      case "custom":
        // Keep current dates
        return;
    }

    applyDateRange(start, end);
  };

  const handleCalendarSelect = (range: { from?: Date; to?: Date } | undefined) => {
    if (!range) return;
    
    if (range.from && !range.to) {
      // Only start date selected
      setStartDate(range.from);
      setEndDate(undefined);
    } else if (range.from && range.to) {
      // Both dates selected
      setStartDate(range.from);
      setEndDate(range.to);
      applyDateRange(range.from, range.to);
      setIsOpen(false);
    }
  };

  const formatDateRange = () => {
    if (startDate && endDate) {
      return `${format(startDate, "MMM d")} - ${format(endDate, "MMM d, yyyy")}`;
    }
    if (startDate) {
      return format(startDate, "MMM d, yyyy");
    }
    return "Select date range";
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="lg"
          className={cn(
            "w-[280px] justify-start text-left font-normal",
            !startDate && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {formatDateRange()}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-4 space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Quick Select</label>
            <Select value={preset} onValueChange={handlePresetChange}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select preset" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="day">Today</SelectItem>
                <SelectItem value="week">Last 7 Days</SelectItem>
                <SelectItem value="month">Last 30 Days</SelectItem>
                <SelectItem value="custom">Custom Range</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {preset === "custom" && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Custom Range</label>
              <CalendarComponent
                mode="range"
                selected={{
                  from: startDate,
                  to: endDate,
                }}
                onSelect={handleCalendarSelect}
                numberOfMonths={2}
                defaultMonth={startDate}
              />
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

