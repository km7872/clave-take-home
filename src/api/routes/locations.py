"""
API routes for location analytics.
"""
from fastapi import APIRouter, Query
from typing import Optional, List
from datetime import datetime
from src.api.models import LocationComparisonResponse
from src.api.services import locations_service

router = APIRouter()


@router.get("/comparison")
async def get_location_comparison(
    locations: str = Query(..., description="Comma-separated location names or IDs"),
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    metric: str = Query("revenue", description="Metric: revenue or orders")
):
    """Compare performance across multiple locations."""
    location_list = [loc.strip() for loc in locations.split(",")]
    result = locations_service.compare_locations(
        locations=location_list,
        start_date=start_date,
        end_date=end_date,
        metric=metric
    )
    return result


@router.get("/performance")
async def get_location_performance(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)")
):
    """Get performance ranking for all locations."""
    result = locations_service.get_location_performance(start_date=start_date, end_date=end_date)
    return result


@router.get("/hourly-pattern")
async def get_hourly_pattern(
    location_id: str = Query(..., description="Location ID"),
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)")
):
    """Get hourly sales patterns for a location."""
    result = locations_service.get_hourly_pattern(
        location_id=location_id,
        start_date=start_date,
        end_date=end_date
    )
    return result

