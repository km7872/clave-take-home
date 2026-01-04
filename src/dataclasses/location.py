"""
Location dataclass model.
"""
from dataclasses import dataclass
from typing import Optional
from src.dataclasses.address import Address


@dataclass
class Location:
    """Location model: id, name, address fields, timezone, status, type, merchant_id"""
    id: str
    name: str
    timezone: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    merchant_id: Optional[str] = None

