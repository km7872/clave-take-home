from dataclasses import dataclass
from typing import Optional

@dataclass
class ItemLocMapping:
    """ItemLocMapping model: item_id, location_id"""
    item_id: str
    location_id: str