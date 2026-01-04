"""
Order dataclass model.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from src.dataclasses.fulfillment import Fulfillment


@dataclass
class Order:
    """Order model: id, location_id, ref_id, source, created_at, updated_at, closed_at, fulfillments, tipAmount, tipAmount_cur, tax fields"""
    id: str
    location_id: str
    ref_id: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    tip_amount: Optional[float] = None 
    tip_amount_currency: str = "USD"
    tax_amount: Optional[float] = None
    tax_currency: str = "USD"
    total_money: Optional[float] = None
    total_money_currency: str = "USD"


