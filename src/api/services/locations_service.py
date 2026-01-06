"""
Service for location analytics.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.db.dbConnect import db


def compare_locations(locations: List[str], start_date: datetime, end_date: datetime, metric: str = "revenue") -> Dict[str, Any]:
    """
    Compare performance across multiple locations.
    
    Args:
        locations: List of location names or IDs
        start_date: Start date for the query
        end_date: End date for the query
        metric: revenue or orders
        
    Returns:
        Comparison data for locations
    """
    
    # Get all locations to match names to IDs
    locations_query = db.table("locations").select("id, name").execute()
    all_locations = {loc["id"]: loc["name"] for loc in (locations_query.data or [])}
    all_locations_by_name = {loc["name"]: loc["id"] for loc in (locations_query.data or [])}
    
    # Convert location names to IDs
    location_ids = []
    for loc in locations:
        if loc in all_locations:
            location_ids.append(loc)
        elif loc in all_locations_by_name:
            location_ids.append(all_locations_by_name[loc])
    
    if not location_ids:
        return {
            "data": [],
            "summary": {},
            "metadata": {
                "suggested_visualization": "bar_chart",
                "x_axis": "location_name",
                "y_axis": metric
            }
        }
    
    # Get orders for these locations
    query = db.table("orders").select("total_money, location_id, created_at, locations(name)")
    query = query.in_("location_id", location_ids)
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    response = query.execute()
    orders = response.data if response.data else []
    
    # Group by location
    location_data = {}
    for order in orders:
        location_id = order.get("location_id")
        location_name = all_locations.get(location_id, location_id)
        
        # Extract from nested structure
        if "locations" in order:
            if isinstance(order["locations"], list) and len(order["locations"]) > 0:
                location_name = order["locations"][0].get("name", location_name)
            elif isinstance(order["locations"], dict):
                location_name = order["locations"].get("name", location_name)
        
        if location_id not in location_data:
            location_data[location_id] = {
                "location_id": location_id,
                "location_name": location_name,
                "revenue": 0,
                "order_count": 0
            }
        
        revenue = float(order.get("total_money", 0) or 0)
        location_data[location_id]["revenue"] += revenue
        location_data[location_id]["order_count"] += 1
    
    # Format result
    result = list(location_data.values())
    for loc in result:
        loc["revenue"] = round(loc["revenue"], 2)
        loc["average_order_value"] = round(
            loc["revenue"] / loc["order_count"] if loc["order_count"] > 0 else 0,
            2
        )
    
    # Sort by metric
    if metric == "revenue":
        result.sort(key=lambda x: x["revenue"], reverse=True)
    else:
        result.sort(key=lambda x: x["order_count"], reverse=True)
    
    return {
        "data": result,
        "summary": {
            "total_locations": len(result),
            "total_revenue": round(sum(loc["revenue"] for loc in result), 2),
            "total_orders": sum(loc["order_count"] for loc in result)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "metric": metric,
            "suggested_visualization": "bar_chart",
            "x_axis": "location_name",
            "y_axis": metric
        }
    }


def get_location_performance(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Get performance ranking for all locations.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        
    Returns:
        All locations ranked by performance
    """
    
    # Get all locations with their orders
    query = db.table("orders").select("total_money, location_id, created_at, locations(name)")
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    response = query.execute()
    orders = response.data if response.data else []
    
    # Group by location
    location_data = {}
    for order in orders:
        location_id = order.get("location_id")
        location_name = location_id
        
        if "locations" in order:
            if isinstance(order["locations"], list) and len(order["locations"]) > 0:
                location_name = order["locations"][0].get("name", location_name)
            elif isinstance(order["locations"], dict):
                location_name = order["locations"].get("name", location_name)
        
        if location_id not in location_data:
            location_data[location_id] = {
                "location_id": location_id,
                "location_name": location_name,
                "revenue": 0,
                "order_count": 0
            }
        
        revenue = float(order.get("total_money", 0) or 0)
        location_data[location_id]["revenue"] += revenue
        location_data[location_id]["order_count"] += 1
    
    # Format and sort
    result = list(location_data.values())
    for loc in result:
        loc["revenue"] = round(loc["revenue"], 2)
        loc["average_order_value"] = round(
            loc["revenue"] / loc["order_count"] if loc["order_count"] > 0 else 0,
            2
        )
    
    result.sort(key=lambda x: x["revenue"], reverse=True)
    
    return {
        "data": result,
        "summary": {
            "total_locations": len(result),
            "total_revenue": round(sum(loc["revenue"] for loc in result), 2)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "bar_chart",
            "x_axis": "location_name",
            "y_axis": "revenue"
        }
    }


def get_hourly_pattern(location_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Get hourly sales patterns for a location.
    
    Args:
        location_id: Location ID
        start_date: Start date for the query
        end_date: End date for the query
        
    Returns:
        Hourly pattern data
    """
    
    query = db.table("orders").select("total_money, created_at")
    query = query.eq("location_id", location_id)
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
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
    
    return {
        "data": result,
        "summary": {
            "peak_hour": max(result, key=lambda x: x["revenue"])["hour"],
            "total_revenue": round(sum(item["revenue"] for item in result), 2)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "line_chart",
            "x_axis": "hour",
            "y_axis": "revenue"
        }
    }

