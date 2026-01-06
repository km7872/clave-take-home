import { createContext, useContext, useState, ReactNode } from "react";

interface DateRange {
  startDate: string; // ISO format
  endDate: string; // ISO format
}

interface DateRangeContextType {
  dateRange: DateRange;
  setDateRange: (range: DateRange) => void;
}

const DateRangeContext = createContext<DateRangeContextType | undefined>(undefined);

// Default date range (Jan 1-4, 2025)
const getDefaultDateRange = (): DateRange => {
  const start = new Date("2025-01-01T00:00:00Z");
  const end = new Date("2025-01-04T23:59:59Z");
  return {
    startDate: start.toISOString(),
    endDate: end.toISOString(),
  };
};

export function DateRangeProvider({ children }: { children: ReactNode }) {
  const [dateRange, setDateRange] = useState<DateRange>(getDefaultDateRange());

  return (
    <DateRangeContext.Provider value={{ dateRange, setDateRange }}>
      {children}
    </DateRangeContext.Provider>
  );
}

export function useDateRange() {
  const context = useContext(DateRangeContext);
  if (context === undefined) {
    throw new Error("useDateRange must be used within a DateRangeProvider");
  }
  return context;
}

