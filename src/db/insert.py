"""
Database insert operations.
"""
from typing import List, Dict, Any
from dataclasses import asdict
from datetime import datetime
from src.dataclasses.location import Location
from src.dataclasses.address import Address
from src.dataclasses.category import Category
from src.dataclasses.item import Item
from src.dataclasses.item_variation import ItemVariation
from src.dataclasses.item_loc_mapping import ItemLocMapping
from src.dataclasses.order import Order
from src.dataclasses.order_detail import OrderDetail
from src.dataclasses.fulfillment import Fulfillment
from src.dataclasses.payment import Payment
from src.dataclasses.card_details import CardDetails
from src.dataclasses.cash_details import CashDetails
from src.db.dbConnect import db


def _serialize_datetime(obj: Any) -> Any:
    """Convert datetime objects to ISO format strings for JSON serialization."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def _prepare_data(data_dict: Dict, exclude_id: bool = False) -> Dict:
    """Prepare data dictionary: remove None values and serialize datetime objects."""
    result = {}
    for k, v in data_dict.items():
        if v is not None and (not exclude_id or k != 'id'):
            result[k] = _serialize_datetime(v)
    return result


def insert_locations(locations: List[Location]) -> tuple:
    """
    Insert locations into Supabase locations table.
    
    Args:
        locations: List of Location dataclass objects
        
    Returns:
        Tuple of (response dict, status code)
    """
    if not locations:
        return {"error": "No locations to insert"}, 400
    
    # Convert Location dataclasses to dictionaries
    locations_data = []
    for location in locations:
        location_dict = asdict(location)
        # Remove None values and serialize datetime objects
        location_dict = _prepare_data(location_dict)
        locations_data.append(location_dict)
    
    try:
        # Insert locations into Supabase
        # created_at and updated_at are auto-set by the database
        response = db.table('locations').insert(locations_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_addresses(addresses: List[Address]) -> tuple:
    """Insert addresses into Supabase addresses table."""
    if not addresses:
        return {"error": "No addresses to insert"}, 400
    
    addresses_data = []
    for address in addresses:
        address_dict = asdict(address)
        # Remove None values, exclude id (auto-generated UUID), and serialize datetime objects
        address_dict = _prepare_data(address_dict, exclude_id=True)
        addresses_data.append(address_dict)
    
    try:
        response = db.table('addresses').insert(addresses_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_categories(categories: List[Category]) -> tuple:
    """Insert categories into Supabase categories table."""
    if not categories:
        return {"error": "No categories to insert"}, 400
    
    categories_data = []
    for category in categories:
        category_dict = asdict(category)
        category_dict = _prepare_data(category_dict)
        categories_data.append(category_dict)
    
    try:
        response = db.table('categories').insert(categories_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_items(items: List[Item]) -> tuple:
    """Insert items into Supabase items table."""
    if not items:
        return {"error": "No items to insert"}, 400
    
    items_data = []
    for item in items:
        item_dict = asdict(item)
        item_dict = _prepare_data(item_dict)
        items_data.append(item_dict)
    
    try:
        response = db.table('items').insert(items_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_item_variations(item_variations: List[ItemVariation]) -> tuple:
    """Insert item variations into Supabase item_variations table."""
    if not item_variations:
        return {"error": "No item variations to insert"}, 400
    
    variations_data = []
    for variation in item_variations:
        variation_dict = asdict(variation)
        variation_dict = _prepare_data(variation_dict)
        variations_data.append(variation_dict)
    
    try:
        response = db.table('item_variations').insert(variations_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_item_location_mapping(mappings: List[ItemLocMapping]) -> tuple:
    """Insert item location mappings into Supabase item_location_mapping table."""
    if not mappings:
        return {"error": "No item location mappings to insert"}, 400
    
    mappings_data = []
    for mapping in mappings:
        mapping_dict = asdict(mapping)
        # Remove None values, exclude id (auto-generated UUID), and serialize datetime objects
        mapping_dict = _prepare_data(mapping_dict, exclude_id=True)
        mappings_data.append(mapping_dict)
    
    try:
        response = db.table('item_location_mapping').insert(mappings_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_orders(orders: List[Order]) -> tuple:
    """Insert orders into Supabase orders table."""
    if not orders:
        return {"error": "No orders to insert"}, 400
    
    orders_data = []
    for order in orders:
        order_dict = asdict(order)
        # Remove None values and serialize datetime objects
        order_dict = _prepare_data(order_dict)
        orders_data.append(order_dict)
    
    try:
        response = db.table('orders').insert(orders_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_order_details(order_details: List[OrderDetail]) -> tuple:
    """Insert order details into Supabase order_details table."""
    if not order_details:
        return {"error": "No order details to insert"}, 400
    
    details_data = []
    for detail in order_details:
        detail_dict = asdict(detail)
        # Include id (UUID string), remove None values, and serialize datetime objects
        detail_dict = _prepare_data(detail_dict)
        details_data.append(detail_dict)
    
    try:
        response = db.table('order_details').insert(details_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_fulfillments(fulfillments: List[Fulfillment]) -> tuple:
    """Insert fulfillments into Supabase fulfillments table."""
    if not fulfillments:
        return {"error": "No fulfillments to insert"}, 400
    
    fulfillments_data = []
    for fulfillment in fulfillments:
        fulfillment_dict = asdict(fulfillment)
        # Remove None values, exclude id (auto-generated UUID), and serialize datetime objects
        fulfillment_dict = _prepare_data(fulfillment_dict, exclude_id=True)
        fulfillments_data.append(fulfillment_dict)
    
    try:
        response = db.table('fulfillments').insert(fulfillments_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_payments(payments: List[Payment]) -> tuple:
    """Insert payments into Supabase payments table."""
    if not payments:
        return {"error": "No payments to insert"}, 400
    
    payments_data = []
    for payment in payments:
        payment_dict = asdict(payment)
        # Remove None values and serialize datetime objects
        payment_dict = _prepare_data(payment_dict)
        payments_data.append(payment_dict)
    
    try:
        response = db.table('payments').insert(payments_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_card_details(card_details: List[CardDetails]) -> tuple:
    """Insert card details into Supabase card_details table."""
    if not card_details:
        return {"error": "No card details to insert"}, 400
    
    details_data = []
    for detail in card_details:
        detail_dict = asdict(detail)
        # Remove None values, exclude id (auto-generated UUID), and serialize datetime objects
        detail_dict = _prepare_data(detail_dict, exclude_id=True)
        details_data.append(detail_dict)
    
    try:
        response = db.table('card_details').insert(details_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


def insert_cash_details(cash_details: List[CashDetails]) -> tuple:
    """Insert cash details into Supabase cash_details table."""
    if not cash_details:
        return {"error": "No cash details to insert"}, 400
    
    details_data = []
    for detail in cash_details:
        detail_dict = asdict(detail)
        # Remove None values, exclude id (auto-generated UUID), and serialize datetime objects
        detail_dict = _prepare_data(detail_dict, exclude_id=True)
        details_data.append(detail_dict)
    
    try:
        response = db.table('cash_details').insert(details_data).execute()
        return {"success": True, "data": response.data, "count": len(response.data) if response.data else 0}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500