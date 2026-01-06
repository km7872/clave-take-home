"""
API routes for time-based analysis.
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from src.api.models import TimePatternResponse
from src.api.services import time_service

router = APIRouter()


@router.get("/peak-hours", response_model=TimePatternResponse)
async def get_peak_hours(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get busiest hours of the day."""
    result = time_service.get_peak_hours(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )
    return TimePatternResponse(**result)


@router.get("/day-of-week")
async def get_day_of_week_analysis(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get performance by day of week."""
    result = time_service.get_day_of_week_analysis(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )
    return result

