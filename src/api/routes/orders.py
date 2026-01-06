"""
API routes for orders and fulfillment.
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from src.api.models import FulfillmentBreakdownResponse
from src.api.services import orders_service

router = APIRouter()


@router.get("/fulfillment-breakdown")
async def get_fulfillment_breakdown(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get breakdown of orders by fulfillment type (DINE_IN, PICKUP, DELIVERY)."""
    result = orders_service.get_fulfillment_breakdown(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )
    return result


@router.get("/average-order-value")
async def get_average_order_value(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get average order value trends."""
    result = orders_service.get_average_order_value(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )
    return result

