"""
Service for time-based analysis.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.db.dbConnect import db


def get_peak_hours(start_date: datetime, end_date: datetime, location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get busiest hours of the day.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        location_id: Optional location filter
        
    Returns:
        Hourly performance data
    """
    
    query = db.table("orders").select("total_money, created_at")
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    if location_id:
        query = query.eq("location_id", location_id)
    
    response = query.execute()
    orders = response.data if response.data else []
    
    # Group by hour
    hourly_data = {hour: {"hour": hour, "revenue": 0, "order_count": 0} for hour in range(24)}
    
    for order in orders:
        created_at = order.get("created_at")
        if not created_at:
            continue
        
        try:
            order_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            hour = order_date.hour
        except:
            continue
        
        revenue = float(order.get("total_money", 0) or 0)
        hourly_data[hour]["revenue"] += revenue
        hourly_data[hour]["order_count"] += 1
    
    # Format result
    result = list(hourly_data.values())
    for item in result:
        item["revenue"] = round(item["revenue"], 2)
    
    peak_hour_data = max(result, key=lambda x: x["revenue"])
    
    return {
        "data": result,
        "summary": {
            "peak_hour": peak_hour_data["hour"],
            "peak_hour_revenue": peak_hour_data["revenue"],
            "total_revenue": round(sum(item["revenue"] for item in result), 2)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "line_chart",
            "x_axis": "hour",
            "y_axis": "revenue"
        }
    }


def get_day_of_week_analysis(start_date: datetime, end_date: datetime, location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get performance by day of week.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        location_id: Optional location filter
        
    Returns:
        Day of week performance data
    """
    
    query = db.table("orders").select("total_money, created_at")
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    if location_id:
        query = query.eq("location_id", location_id)
    
    response = query.execute()
    orders = response.data if response.data else []
    
    # Group by day of week (0=Monday, 6=Sunday)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_data = {i: {"day": day_names[i], "day_number": i, "revenue": 0, "order_count": 0} for i in range(7)}
    
    for order in orders:
        created_at = order.get("created_at")
        if not created_at:
            continue
        
        try:
            order_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            day_of_week = order_date.weekday()  # 0=Monday, 6=Sunday
        except:
            continue
        
        revenue = float(order.get("total_money", 0) or 0)
        daily_data[day_of_week]["revenue"] += revenue
        daily_data[day_of_week]["order_count"] += 1
    
    # Format result
    result = list(daily_data.values())
    for item in result:
        item["revenue"] = round(item["revenue"], 2)
        item["average_order_value"] = round(
            item["revenue"] / item["order_count"] if item["order_count"] > 0 else 0,
            2
        )
    
    best_day = max(result, key=lambda x: x["revenue"])
    
    return {
        "data": result,
        "summary": {
            "best_day": best_day["day"],
            "best_day_revenue": best_day["revenue"],
            "total_revenue": round(sum(item["revenue"] for item in result), 2)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "bar_chart",
            "x_axis": "day",
            "y_axis": "revenue"
        }
    }

