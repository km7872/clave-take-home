"""
API routes for product performance.
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from src.api.models import ProductPerformanceResponse
from src.api.services import products_service

router = APIRouter()


@router.get("/top-selling", response_model=ProductPerformanceResponse)
async def get_top_selling_products(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    limit: int = Query(10, description="Number of products to return"),
    metric: str = Query("revenue", description="Metric: revenue or quantity"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get top selling products by revenue or quantity."""
    result = products_service.get_top_selling_products(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        metric=metric,
        location_id=location_id
    )
    return ProductPerformanceResponse(**result)


# @router.get("/category-performance")
async def get_category_performance(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    location_id: Optional[str] = Query(None, description="Filter by location ID")
):
    """Get performance by product category."""
    result = products_service.get_category_performance(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id
    )
    return result

