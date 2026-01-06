"""
API routes for payment analytics.
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from src.api.models import PaymentMethodResponse
from src.api.services import payments_service

router = APIRouter()


@router.get("/method-breakdown", response_model=PaymentMethodResponse)
async def get_payment_method_breakdown(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get breakdown of payments by method (CARD, CASH, etc.)."""
    result = payments_service.get_payment_method_breakdown(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )
    return PaymentMethodResponse(**result)


@router.get("/tips-analysis")
async def get_tips_analysis(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get tips analysis and trends."""
    result = payments_service.get_tips_analysis(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )
    return result

