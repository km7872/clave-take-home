"""
Category dataclass model.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Category:
    """Category model: id, name"""
    id: str
    name: str
    display_name: Optional[str] = None

