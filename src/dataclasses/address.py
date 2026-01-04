"""
Address dataclass model.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Address:
    """Address fields for location"""
    location_id : str
    address_line_1: Optional[str] = None
    locality: Optional[str] = None
    administrative_district_level_1: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

