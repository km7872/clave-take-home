"""
API routes for revenue and sales metrics.
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from src.api.models import MetricResponse, RevenueTrendResponse
from src.api.services import metrics_service

router = APIRouter()


@router.get("/revenue", response_model=MetricResponse)
async def get_revenue(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get total revenue for a date range."""
    result = metrics_service.get_revenue(start_date=start_date, end_date=end_date, location_id=location_id)
    return MetricResponse(
        value=result["value"],
        count=result["count"],
        period=result["period"],
        location_id=result.get("location_id"),
        location_name=None
    )


@router.get("/revenue-by-location")
async def get_revenue_by_location(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)")
):
    """Get revenue grouped by location."""
    result = metrics_service.get_revenue_by_location(start_date=start_date, end_date=end_date)
    return {
        "data": result,
        "metadata": {
            "suggested_visualization": "bar_chart",
            "x_axis": "location_name",
            "y_axis": "revenue"
        }
    }


@router.get("/revenue-trend", response_model=RevenueTrendResponse)
async def get_revenue_trend(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    granularity: str = Query("day", description="Time granularity: hour, day"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get revenue trend over time."""
    result = metrics_service.get_revenue_trend(
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        location_id=location_id
    )
    return RevenueTrendResponse(**result)

