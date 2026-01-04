"""
Fulfillment dataclass model.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Fulfillment:
    """Fulfillment fields for orders"""
    order_id: str
    uid: Optional[str] = None
    type: Optional[str] = None  # DINE_IN, PICKUP, DELIVERY, etc. (can be moved to enum)
    state: Optional[str] = None

