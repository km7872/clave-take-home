"""
Payment dataclass model.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from src.dataclasses.card_details import CardDetails
from src.dataclasses.cash_details import CashDetails


@dataclass
class Payment:
    """Payment model: id, order_id, location_id, created_at, updated_at, amt, amt_curr, tipAmount, tipAmount_cur, totalMoney, totalMoney_cur, source_type, status, card/cash"""
    id: str
    order_id: str
    location_id: str
    amount_currency: str
    tip_amount_currency: str
    total_money_currency: str = "USD"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    amount: Optional[float] = None
    tip_amount: Optional[float] = None 
    total_money: Optional[float] = None
    source_type: Optional[str] = None  # CARD, CASH, etc. (can be moved to enum)
    status: Optional[str] = None

