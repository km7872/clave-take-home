import { DollarSign, TrendingUp, ShoppingBag } from "lucide-react";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { ChartCard } from "@/components/dashboard/ChartCard";
import { RevenueTrendChart } from "@/components/dashboard/charts/RevenueTrendChart";
import { RevenueByLocationChart } from "@/components/dashboard/charts/RevenueByLocationChart";
import { TopSellingChart } from "@/components/dashboard/charts/TopSellingChart";
import { PaymentMethodsChart } from "@/components/dashboard/charts/PaymentMethodsChart";
import { FulfillmentChart } from "@/components/dashboard/charts/FulfillmentChart";
import { PeakHoursChart } from "@/components/dashboard/charts/PeakHoursChart";
import { DateRangeProvider } from "@/contexts/DateRangeContext";

const Index = () => {
  return (
    <DateRangeProvider>
      <div className="min-h-screen bg-background p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          <DashboardHeader />

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <MetricCard
            title="Total Revenue"
            icon={<DollarSign className="h-5 w-5" />}
            insights={[
              "Revenue increased by 12.5% compared to last week",
              "Weekend sales contributed 45% of total revenue",
              "Airport location shows highest revenue growth at 18%",
              "Digital payments drove 73% of total transactions",
            ]}
            delay={100}
            apiEndpoint="/api/metrics/revenue"
          />
          <MetricCard
            title="Total Tips"
            icon={<TrendingUp className="h-5 w-5" />}
            insights={[
              "Average tip rate is 6.8% of total order value",
              "Tips increased during dinner hours (6-9 PM)",
              "Card payments have higher tip rates than cash",
              "Top performing staff earned 2x average tips",
            ]}
            delay={200}
            apiEndpoint="/api/payments/tips-analysis"
          />
          <MetricCard
            title="Avg Order Value"
            icon={<ShoppingBag className="h-5 w-5" />}
            insights={[
              "AOV decreased slightly due to promotional discounts",
              "Combo meals maintain higher AOV at $24.50",
              "Upselling drinks increased AOV by $2.30",
              "Weekend orders have 15% higher AOV than weekdays",
            ]}
            delay={300}
            apiEndpoint="/api/orders/average-order-value"
          />
        </div>

        {/* Main Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartCard
            title="Revenue Trend"
            insights={[
              "Saturday shows peak revenue at $22,100",
              "Mid-week dip suggests opportunity for promotions",
              "Revenue trend is up 15% month-over-month",
              "Friday-Saturday accounts for 35% of weekly revenue",
            ]}
            delay={400}
          >
            <RevenueTrendChart />
          </ChartCard>

          <ChartCard
            title="Revenue by Location"
            insights={[
              "Airport location leads with $52,100 revenue",
              "Campus location has growth potential with student promotions",
              "Downtown location performs well during lunch hours",
              "Mall location shows steady weekend performance",
            ]}
            delay={500}
          >
            <RevenueByLocationChart />
          </ChartCard>
        </div>

        {/* Secondary Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <ChartCard
            title="Top Selling Products"
            insights={[
              "Classic Burger remains #1 bestseller with 1,842 units",
              "Chicken Wings saw 23% growth this week",
              "Fries bundle deals drive volume sales",
              "New Milkshake flavors boosted category by 18%",
            ]}
            delay={600}
            className="lg:col-span-2"
          >
            <TopSellingChart />
          </ChartCard>

          <ChartCard
            title="Peak Hours"
            insights={[
              "Lunch peak (12-1 PM) sees 280 orders/hour",
              "Dinner rush starts earlier on Fridays",
              "Morning breakfast promotion increased 6-8 AM traffic",
              "Late night orders growing with delivery partnerships",
            ]}
            delay={700}
          >
            <PeakHoursChart />
          </ChartCard>
        </div>

        {/* Bottom Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ChartCard
            title="Payment Methods"
            insights={[
              "Card payments dominate at 58% of transactions",
              "Mobile payments growing at 25% monthly rate",
              "Cash transactions declining steadily",
              "Contactless payments up 40% since last quarter",
            ]}
            delay={800}
          >
            <PaymentMethodsChart />
          </ChartCard>

          <ChartCard
            title="Fulfillment Breakdown"
            insights={[
              "Dine-in leads at 42% but delivery growing fast",
              "Takeout orders have lowest wait times",
              "Delivery partnerships increased order volume 30%",
              "Drive-thru expansion could capture more takeout",
            ]}
            delay={900}
          >
            <FulfillmentChart />
          </ChartCard>
        </div>
        </div>
      </div>
    </DateRangeProvider>
  );
};

export default Index;
