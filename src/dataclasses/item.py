"""
Item dataclass model.
"""
from dataclasses import dataclass
from typing import Optional, List
display_name: Optional[str] = None 


@dataclass
class Item:
    """Item model: id, name, description, category_id"""
    id: str
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    display_name: Optional[str] = None

