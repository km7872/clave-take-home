"""
Item variation dataclass model.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class ItemVariation:
    """Item variation model: id, item_id, name, price, price_currency"""
    id: str
    item_id: str
    name: str
    price_currency: str
    price: float
    display_name: Optional[str] = None

