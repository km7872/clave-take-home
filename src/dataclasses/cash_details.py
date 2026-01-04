"""
Cash payment details dataclass model.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CashDetails:
    """Cash payment details: payment_id, cash detail fields"""
    payment_id: str
    buyer_supplied_currency: str
    change_back_currency: str
    buyer_supplied_money: Optional[float] = None
    change_back_money: Optional[float] = None

