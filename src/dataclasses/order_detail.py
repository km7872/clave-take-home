"""
Order detail dataclass model.
"""
from dataclasses import dataclass


@dataclass
class OrderDetail:
    """Order details model: id, order_id, itemvar_id, qty, grossamt, grossamt_cur, totalamt, totalamt_cur"""
    id: str
    order_id: str
    itemvar_id: str  # Item variation ID
    qty: int
    gross_amount_currency: str
    gross_amount: float
    total_amount_currency: str
    total_amount: float

