"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class MetricResponse(BaseModel):
    """Response model for metric endpoints."""
    value: float
    count: Optional[int] = None
    period: str
    location_id: Optional[str] = None
    location_name: Optional[str] = None


class RevenueTrendResponse(BaseModel):
    """Response model for revenue trends."""
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]


class ProductPerformanceResponse(BaseModel):
    """Response model for product performance."""
    data: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]


class LocationComparisonResponse(BaseModel):
    """Response model for location comparison."""
    data: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]


class FulfillmentBreakdownResponse(BaseModel):
    """Response model for fulfillment breakdown."""
    data: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]


class PaymentMethodResponse(BaseModel):
    """Response model for payment methods."""
    data: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]


class TimePatternResponse(BaseModel):
    """Response model for time-based patterns."""
    data: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]

