"""
Service for payment analytics.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.db.dbConnect import db


def get_payment_method_breakdown(start_date: datetime, end_date: datetime, location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get breakdown of payments by method.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        location_id: Optional location filter
        
    Returns:
        Payment method breakdown
    """
    
    query = db.table("payments").select("amount, source_type, location_id, created_at")
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    if location_id:
        query = query.eq("location_id", location_id)
    
    response = query.execute()
    payments = response.data if response.data else []
    
    # Group by payment method
    method_data = {}
    
    for payment in payments:
        source_type = payment.get("source_type", "UNKNOWN") or "UNKNOWN"
        
        if source_type not in method_data:
            method_data[source_type] = {
                "method": source_type,
                "amount": 0,
                "payment_count": 0
            }
        
        amount = float(payment.get("amount", 0) or 0)
        method_data[source_type]["amount"] += amount
        method_data[source_type]["payment_count"] += 1
    
    # Format result
    result = list(method_data.values())
    total_amount = sum(item["amount"] for item in result)
    
    for item in result:
        item["amount"] = round(item["amount"], 2)
        item["percentage"] = round(
            (item["amount"] / total_amount * 100) if total_amount > 0 else 0,
            2
        )
    
    return {
        "data": result,
        "summary": {
            "total_amount": round(total_amount, 2),
            "total_payments": sum(item["payment_count"] for item in result)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "pie_chart",
            "x_axis": "method",
            "y_axis": "amount"
        }
    }


def get_tips_analysis(start_date: datetime, end_date: datetime, location_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get tips analysis and trends.
    
    Args:
        start_date: Start date for the query
        end_date: End date for the query
        location_id: Optional location filter
        
    Returns:
        Tips analysis data
    """
    
    query = db.table("payments").select("amount, tip_amount, location_id, created_at")
    query = query.gte("created_at", start_date.isoformat())
    query = query.lte("created_at", end_date.isoformat())
    
    if location_id:
        query = query.eq("location_id", location_id)
    
    response = query.execute()
    payments = response.data if response.data else []
    
    total_tips = 0
    total_amount = 0
    tip_count = 0
    
    for payment in payments:
        amount = float(payment.get("amount", 0) or 0)
        tip = float(payment.get("tip_amount", 0) or 0)
        
        total_amount += amount
        if tip > 0:
            total_tips += tip
            tip_count += 1
    
    tip_percentage = (total_tips / total_amount * 100) if total_amount > 0 else 0
    average_tip = total_tips / tip_count if tip_count > 0 else 0
    
    return {
        "data": {
            "total_tips": round(total_tips, 2),
            "total_amount": round(total_amount, 2),
            "tip_percentage": round(tip_percentage, 2),
            "average_tip": round(average_tip, 2),
            "tipped_payments": tip_count,
            "total_payments": len(payments)
        },
        "summary": {
            "tip_rate": round((tip_count / len(payments) * 100) if payments else 0, 2)
        },
        "metadata": {
            "period": f"{start_date.date()} to {end_date.date()}",
            "suggested_visualization": "metric_card"
        }
    }

