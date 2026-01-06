"""
Service for revenue and sales metrics.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from src.db.dbConnect import db


def get_revenue(start_date: datetime, end_date: datetime, location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get total revenue for a date range.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        location_id: Optional location filter
        
    Returns:
        Dictionary with revenue, count, and period info
    """
    
    query = db.table("orders").select("total_money, location_id, created_at")
    
    if location_id:
        query = query.eq("location_id", location_id)
    
    # Filter by date range
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    response = query.execute()
    orders = response.data if response.data else []
    
    total_revenue = sum(float(order.get("total_money", 0) or 0) for order in orders)
    order_count = len(orders)
    avg_order_value = total_revenue / order_count if order_count > 0 else 0
    
    return {
        "value": round(total_revenue, 2),
        "count": order_count,
        "average": round(avg_order_value, 2),
        "period": f"{start_date.date()} to {end_date.date()}",
        "location_id": location_id
    }


def get_revenue_by_location(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Get revenue grouped by location.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        
    Returns:
        List of location revenue data
    """
    
    # Get orders with location info
    query = db.table("orders").select("total_money, location_id, created_at, locations(name)")
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    response = query.execute()
    orders = response.data if response.data else []
    
    # Group by location name (not location_id)
    location_revenue = {}
    for order in orders:
        location_name = None
        
        # Extract location name from nested structure
        if "locations" in order and isinstance(order["locations"], list) and len(order["locations"]) > 0:
            location_name = order["locations"][0].get("name")
        elif "locations" in order and isinstance(order["locations"], dict):
            location_name = order["locations"].get("name")
        
        # Use location_name as key (fallback to "Unknown" if missing)
        location_key = location_name or "Unknown"
        
        if location_key not in location_revenue:
            location_revenue[location_key] = {
                "location_name": location_key,
                "revenue": 0,
                "order_count": 0
            }
        
        revenue = float(order.get("total_money", 0) or 0)
        location_revenue[location_key]["revenue"] += revenue
        location_revenue[location_key]["order_count"] += 1
    
    # Calculate averages and format
    result = []
    for loc_data in location_revenue.values():
        loc_data["revenue"] = round(loc_data["revenue"], 2)
        loc_data["average_order_value"] = round(
            loc_data["revenue"] / loc_data["order_count"] if loc_data["order_count"] > 0 else 0,
            2
        )
        result.append(loc_data)
    
    # Sort by revenue descending
    result.sort(key=lambda x: x["revenue"], reverse=True)
    
    return result


def get_revenue_trend(start_date: datetime, end_date: datetime, granularity: str = "day", location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get revenue trend over time.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        granularity: hour, day
        location_id: Optional location filter
        
    Returns:
        Time series data for revenue
    """
    
    query = db.table("orders").select("total_money, location_id, created_at")
    
    if location_id:
        query = query.eq("location_id", location_id)
    
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    query = query.order("created_at", desc=False)
    
    response = query.execute()
    orders = response.data if response.data else []
    
    # Group by time granularity
    time_buckets = {}
    
    for order in orders:
        created_at = order.get("created_at")
        if not created_at:
            continue
        
        try:
            order_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except:
            continue
        
        if granularity == "hour":
            bucket_key = order_date.strftime("%Y-%m-%d %H:00")
        else:  # day
            bucket_key = order_date.strftime("%Y-%m-%d")
        
        if bucket_key not in time_buckets:
            time_buckets[bucket_key] = {
                "period": bucket_key,
                "revenue": 0,
                "order_count": 0
            }
        
        revenue = float(order.get("total_money", 0) or 0)
        time_buckets[bucket_key]["revenue"] += revenue
        time_buckets[bucket_key]["order_count"] += 1
    
    # Convert to list and sort
    data = list(time_buckets.values())
    data.sort(key=lambda x: x["period"])
    
    # Calculate summary
    total_revenue = sum(item["revenue"] for item in data)
    total_orders = sum(item["order_count"] for item in data)
    
    return {
        "data": data,
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "average_revenue": round(total_revenue / len(data) if data else 0, 2)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "granularity": granularity,
            "suggested_visualization": "line_chart",
            "x_axis": "period",
            "y_axis": "revenue"
        }
    }

