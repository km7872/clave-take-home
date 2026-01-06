"""
Service for orders and fulfillment analytics.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.db.dbConnect import db


def get_fulfillment_breakdown(start_date: datetime, end_date: datetime, location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get breakdown of orders by fulfillment type.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        location_id: Optional location filter
        
    Returns:
        Fulfillment type breakdown
    """
    
    # Get orders with fulfillments
    query = db.table("orders").select("total_money, location_id, created_at, fulfillments(type)")
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    if location_id:
        query = query.eq("location_id", location_id)
    
    response = query.execute()
    orders = response.data if response.data else []
    
    # Group by fulfillment type
    fulfillment_data = {}
    
    for order in orders:
        fulfillments = order.get("fulfillments", [])
        if isinstance(fulfillments, list) and len(fulfillments) > 0:
            fulfillment = fulfillments[0]
        elif isinstance(fulfillments, dict):
            fulfillment = fulfillments
        else:
            fulfillment_type = "UNKNOWN"
            fulfillments = [{"type": fulfillment_type}]
            fulfillment = fulfillments[0] if fulfillments else {}
        
        fulfillment_type = fulfillment.get("type", "UNKNOWN") or "UNKNOWN"
        
        if fulfillment_type not in fulfillment_data:
            fulfillment_data[fulfillment_type] = {
                "type": fulfillment_type,
                "revenue": 0,
                "order_count": 0
            }
        
        revenue = float(order.get("total_money", 0) or 0)
        fulfillment_data[fulfillment_type]["revenue"] += revenue
        fulfillment_data[fulfillment_type]["order_count"] += 1
    
    # Format result
    result = list(fulfillment_data.values())
    total_revenue = sum(item["revenue"] for item in result)
    total_orders = sum(item["order_count"] for item in result)
    
    for item in result:
        item["revenue"] = round(item["revenue"], 2)
        item["percentage"] = round(
            (item["revenue"] / total_revenue * 100) if total_revenue > 0 else 0,
            2
        )
    
    return {
        "data": result,
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "pie_chart",
            "x_axis": "type",
            "y_axis": "revenue"
        }
    }


def get_average_order_value(start_date: datetime, end_date: datetime, location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get average order value trends.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        location_id: Optional location filter
        
    Returns:
        AOV data over time
    """
    
    query = db.table("orders").select("total_money, created_at")
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    if location_id:
        query = query.eq("location_id", location_id)
    
    query = query.order("created_at", desc=False)
    
    response = query.execute()
    orders = response.data if response.data else []
    
    # Group by day
    daily_data = {}
    
    for order in orders:
        created_at = order.get("created_at")
        if not created_at:
            continue
        
        try:
            order_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            date_key = order_date.strftime("%Y-%m-%d")
        except:
            continue
        
        if date_key not in daily_data:
            daily_data[date_key] = {
                "date": date_key,
                "total_revenue": 0,
                "order_count": 0,
                "average_order_value": 0
            }
        
        revenue = float(order.get("total_money", 0) or 0)
        daily_data[date_key]["total_revenue"] += revenue
        daily_data[date_key]["order_count"] += 1
    
    # Calculate AOV
    result = list(daily_data.values())
    for item in result:
        item["total_revenue"] = round(item["total_revenue"], 2)
        item["average_order_value"] = round(
            item["total_revenue"] / item["order_count"] if item["order_count"] > 0 else 0,
            2
        )
    
    result.sort(key=lambda x: x["date"])
    
    overall_aov = round(
        sum(item["total_revenue"] for item in result) / sum(item["order_count"] for item in result)
        if sum(item["order_count"] for item in result) > 0 else 0,
        2
    )
    
    return {
        "data": result,
        "summary": {
            "overall_aov": overall_aov,
            "total_revenue": round(sum(item["total_revenue"] for item in result), 2),
            "total_orders": sum(item["order_count"] for item in result)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "line_chart",
            "x_axis": "date",
            "y_axis": "average_order_value"
        }
    }

