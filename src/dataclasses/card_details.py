"""
Card payment details dataclass model.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CardDetails:
    """Card payment details: payment_id, card detail fields"""
    payment_id: str
    status: Optional[str] = None
    card_brand: Optional[str] = None
    last_4: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    entry_method: Optional[str] = None

