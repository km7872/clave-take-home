"""
Service for product performance queries.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.db.dbConnect import db


def get_top_selling_products(start_date: datetime, end_date: datetime, limit: int = 10, metric: str = "revenue", location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get top selling products by revenue or quantity.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        limit: Number of products to return
        metric: revenue or quantity
        location_id: Optional location filter
        
    Returns:
        Top products with aggregated data
    """
    # Get orders first to filter by date and location
    orders_query = db.table("orders").select("id, location_id, created_at")
    orders_query = orders_query.gte("created_at", start_date.isoformat())
    orders_query = orders_query.lte("created_at", end_date.isoformat())
    
    if location_id:
        orders_query = orders_query.eq("location_id", location_id)
    
    orders_response = orders_query.execute()
    valid_order_ids = {order["id"] for order in (orders_response.data or [])}
    
    if not valid_order_ids:
        return {
            "data": [],
            "summary": {
                "total_products": 0,
                "total_revenue": 0,
                "total_quantity": 0
            },
            "metadata": {
                "period": f"{start_date.date()} to {end_date.date()}",
                "metric": metric,
                "suggested_visualization": "bar_chart",
                "x_axis": "name",
                "y_axis": metric
            }
        }
    
    # Get order details with item variations
    query = db.table("order_details").select(
        "gross_amount, qty, itemvar_id, order_id, item_variations(id, name, item_id, items(name))"
    )
    query = query.in_("order_id", list(valid_order_ids))
    
    response = query.execute()
    order_details = response.data if response.data else []
    
    # Group by item variation
    product_data = {}
    
    for detail in order_details:
        itemvar_id = detail.get("itemvar_id")
        if not itemvar_id:
            continue
        
        # Extract item variation info
        item_variation = detail.get("item_variations")
        if isinstance(item_variation, list) and len(item_variation) > 0:
            item_variation = item_variation[0]
        
        if not item_variation:
            continue
        
        item_id = item_variation.get("item_id")
        variation_name = item_variation.get("name", "")
        
        # Get item name
        item_name = ""
        items = item_variation.get("items")
        if isinstance(items, list) and len(items) > 0:
            item_name = items[0].get("name", "")
        elif isinstance(items, dict):
            item_name = items.get("name", "")
        
        if itemvar_id not in product_data:
            product_data[itemvar_id] = {
                "id": itemvar_id,
                "item_id": item_id,
                "name": variation_name,
                "item_name": item_name,
                "revenue": 0,
                "quantity": 0
            }
        
        gross_amount = float(detail.get("gross_amount", 0) or 0)
        qty = int(detail.get("qty", 0) or 0)
        
        product_data[itemvar_id]["revenue"] += gross_amount
        product_data[itemvar_id]["quantity"] += qty
    
    # Convert to list and sort
    products = list(product_data.values())
    
    if metric == "revenue":
        products.sort(key=lambda x: x["revenue"], reverse=True)
    else:  # quantity
        products.sort(key=lambda x: x["quantity"], reverse=True)
    
    # Limit and round
    top_products = products[:limit]
    for product in top_products:
        product["revenue"] = round(product["revenue"], 2)
    
    return {
        "data": top_products,
        "summary": {
            "total_products": len(products),
            "total_revenue": round(sum(p["revenue"] for p in top_products), 2),
            "total_quantity": sum(p["quantity"] for p in top_products)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "metric": metric,
            "suggested_visualization": "bar_chart",
            "x_axis": "name",
            "y_axis": metric
        }
    }


def get_category_performance(start_date: datetime, end_date: datetime, location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get performance by product category.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        location_id: Optional location filter
        
    Returns:
        Category performance data
    """
    # Get orders first to filter by date and location
    orders_query = db.table("orders").select("id, location_id, created_at")
    orders_query = orders_query.gte("created_at", start_date.isoformat())
    orders_query = orders_query.lte("created_at", end_date.isoformat())
    
    if location_id:
        orders_query = orders_query.eq("location_id", location_id)
    
    orders_response = orders_query.execute()
    valid_order_ids = {order["id"] for order in (orders_response.data or [])}
    
    if not valid_order_ids:
        return {
            "data": [],
            "summary": {
                "total_categories": 0,
                "total_revenue": 0
            },
            "metadata": {
                "period": f"{start_date.date()} to {end_date.date()}",
                "suggested_visualization": "bar_chart",
                "x_axis": "category_name",
                "y_axis": "revenue"
            }
        }
    
    # Get order details with categories
    query = db.table("order_details").select(
        "gross_amount, qty, itemvar_id, order_id, item_variations(item_id, items(category_id, categories(name)))"
    )
    query = query.in_("order_id", list(valid_order_ids))
    
    response = query.execute()
    order_details = response.data if response.data else []
    
    # Group by category
    category_data = {}
    
    for detail in order_details:
        item_variation = detail.get("item_variations")
        if isinstance(item_variation, list) and len(item_variation) > 0:
            item_variation = item_variation[0]
        
        if not item_variation:
            continue
        
        items = item_variation.get("items")
        if isinstance(items, list) and len(items) > 0:
            item = items[0]
        elif isinstance(items, dict):
            item = items
        else:
            continue
        
        categories = item.get("categories")
        if isinstance(categories, list) and len(categories) > 0:
            category = categories[0]
        elif isinstance(categories, dict):
            category = categories
        else:
            continue
        
        category_id = category.get("id") or "uncategorized"
        category_name = category.get("name") or "Uncategorized"
        
        if category_id not in category_data:
            category_data[category_id] = {
                "category_id": category_id,
                "category_name": category_name,
                "revenue": 0,
                "quantity": 0
            }
        
        gross_amount = float(detail.get("gross_amount", 0) or 0)
        qty = int(detail.get("qty", 0) or 0)
        
        category_data[category_id]["revenue"] += gross_amount
        category_data[category_id]["quantity"] += qty
    
    # Convert to list and sort
    categories = list(category_data.values())
    categories.sort(key=lambda x: x["revenue"], reverse=True)
    
    for cat in categories:
        cat["revenue"] = round(cat["revenue"], 2)
    
    return {
        "data": categories,
        "summary": {
            "total_categories": len(categories),
            "total_revenue": round(sum(c["revenue"] for c in categories), 2)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "bar_chart",
            "x_axis": "category_name",
            "y_axis": "revenue"
        }
    }

