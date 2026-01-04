"""
Parser for Square POS JSON data files.
Maps Square data structure to unified models.
"""
import json
from datetime import datetime
from typing import List, Dict, Optional
from src.dataclasses.category import Category
from src.dataclasses.item import Item
from src.dataclasses.item_variation import ItemVariation
from src.dataclasses.location import Location
from src.dataclasses.address import Address
from src.dataclasses.order import Order
from src.dataclasses.order_detail import OrderDetail
from src.dataclasses.fulfillment import Fulfillment
from src.dataclasses.payment import Payment
from src.dataclasses.card_details import CardDetails
from src.dataclasses.cash_details import CashDetails
from src.dataclasses.item_loc_mapping import ItemLocMapping
import uuid

import re

class SquareParser:
    """Parser for Square POS JSON files"""
    
    def __init__(self, catalog_path: str, orders_path: str, payments_path: str, locations_path: str):
        """
        Initialize parser with paths to Square JSON files.
        
        Args:
            catalog_path: Path to catalog.json
            orders_path: Path to orders.json
            payments_path: Path to payments.json
            locations_path: Path to locations.json
        """
        self.catalog_path = catalog_path
        self.orders_path = orders_path
        self.payments_path = payments_path
        self.locations_path = locations_path
        
        # Cache for parsed data
        self._catalog_data = None
        self._orders_data = None
        self._payments_data = None
        self._locations_data = None
    
    def _load_json(self, path: str) -> Dict:
        """Load JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    def _cents_to_dollars(self, cents: Optional[int]) -> Optional[float]:
        """Convert amount from cents to dollars"""
        if cents is None:
            return None
        return cents / 100.0
    
    def remove_emojis(self, text):
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & pictographs
            "\U0001F680-\U0001F6FF"  # Transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # Flags
            "\U00002700-\U000027BF"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)
    
    def parse_categories(self) -> List[Category]:
        """Parse categories from catalog.json"""
        if self._catalog_data is None:
            self._catalog_data = self._load_json(self.catalog_path)
        
        categories = []
        for obj in self._catalog_data.get('objects', []):
            if obj.get('type') == 'CATEGORY':
                name = obj.get('category_data', {}).get('name', '')
                name = self.remove_emojis(name)
                categories.append(Category(
                    id=obj.get('id', ''),
                    name=name
                ))
        
        return categories
    
    def parse_items(self) -> List[Item]:
        """Parse items from catalog.json"""
        if self._catalog_data is None:
            self._catalog_data = self._load_json(self.catalog_path)
        
        items = []
        for obj in self._catalog_data.get('objects', []):
            if obj.get('type') == 'ITEM':
                item_data = obj.get('item_data', {})
                name = item_data.get('name', '')
                name = self.remove_emojis(name)
                items.append(Item(
                    id=obj.get('id', ''),
                    name=name,
                    description=item_data.get('description'),
                    category_id=item_data.get('category_id'), 
                ))
        
        return items
    
    def parse_item_loc_mappings(self):
        if self._catalog_data is None:
            self._catalog_data = self._load_json(self.catalog_path)
        item_loc_mappings = []
        for obj in self._catalog_data.get('objects', []):
            if obj.get('type') == 'ITEM':
                
                location_ids=obj.get('present_at_location_ids', [])
                for locId in location_ids:
                    item_loc_mappings.append(ItemLocMapping(item_id=obj.get('id', ''), location_id=locId))
        
        return item_loc_mappings

    
    def parse_item_variations(self) -> List[ItemVariation]:
        """Parse item variations from catalog.json"""
        if self._catalog_data is None:
            self._catalog_data = self._load_json(self.catalog_path)
        
        variations = []
        
        # Variations can be nested inside items or standalone
        for obj in self._catalog_data.get('objects', []):
            if obj.get('type') == 'ITEM':
                item_data = obj.get('item_data', {})
                item_id = obj.get('id', '')
                
                # Parse variations nested in item
                for var_obj in item_data.get('variations', []):
                    if var_obj.get('type') == 'ITEM_VARIATION':
                        var_data = var_obj.get('item_variation_data', {})
                        price_money = var_data.get('price_money', {})
                        name = var_data.get('name', '')
                        name = self.remove_emojis(name)
                        variations.append(ItemVariation(
                            id=var_obj.get('id', ''),
                            item_id=var_data.get('item_id', item_id),
                            name=name,
                            price_currency=price_money.get('currency', 'USD'),
                            price=self._cents_to_dollars(price_money.get('amount', 0))
                        ))
            
            elif obj.get('type') == 'ITEM_VARIATION':
                # Standalone variation
                var_data = obj.get('item_variation_data', {})
                price_money = var_data.get('price_money', {})
                
                variations.append(ItemVariation(
                    id=obj.get('id', ''),
                    item_id=var_data.get('item_id', ''),
                    name=var_data.get('name', ''),
                    price_currency=price_money.get('currency', 'USD'),
                    price=self._cents_to_dollars(price_money.get('amount', 0))
                ))
        
        return variations
    
    def parse_locations(self) -> List[Location]:
        """Parse locations from locations.json"""
        if self._locations_data is None:
            self._locations_data = self._load_json(self.locations_path)
        
        locations = []
        for loc_data in self._locations_data.get('locations', []):            
            locations.append(Location(
                id=loc_data.get('id', ''),
                name=loc_data.get('name', ''),
                timezone=loc_data.get('timezone'),
                status=loc_data.get('status'),
                type=loc_data.get('type'),
                merchant_id=loc_data.get('merchant_id')
            ))
        
        return locations
    
    def parse_address(self) -> List[Address]:
        """Parse locations from locations.json"""
        if self._locations_data is None:
            self._locations_data = self._load_json(self.locations_path)
        
        addressLst = []
        for loc_data in self._locations_data.get('locations', []):
            address_data = loc_data.get('address', {})
            address = Address(
                location_id=loc_data.get('id', ''),
                address_line_1=address_data.get('address_line_1'),
                locality=address_data.get('locality'),
                administrative_district_level_1=address_data.get('administrative_district_level_1'),
                postal_code=address_data.get('postal_code'),
                country=address_data.get('country')
            )
            addressLst.append(address)

        
        return addressLst
    
    def parse_orders(self) -> List[Order]:
        """Parse orders from orders.json"""
        if self._orders_data is None:
            self._orders_data = self._load_json(self.orders_path)
        
        orders = []
        for order_data in self._orders_data.get('orders', []):
            
            # Parse source
            source_obj = order_data.get('source', {})
            source_name = source_obj.get('name') if source_obj else None
            
            # Parse tip, tax, and total
            tip_money = order_data.get('total_tip_money', {})
            tax_money = order_data.get('total_tax_money', {})
            total_money = order_data.get('total_money', {})
            
            orders.append(Order(
                id=order_data.get('id', ''),
                location_id=order_data.get('location_id', ''),
                ref_id=order_data.get('reference_id'),
                source=source_name,
                created_at=self._parse_datetime(order_data.get('created_at')),
                updated_at=self._parse_datetime(order_data.get('updated_at')),
                closed_at=self._parse_datetime(order_data.get('closed_at')),
                tip_amount=self._cents_to_dollars(tip_money.get('amount')),
                tip_amount_currency=tip_money.get('currency', 'USD'),
                tax_amount=self._cents_to_dollars(tax_money.get('amount')),
                tax_currency=tax_money.get('currency', 'USD'),
                total_money=self._cents_to_dollars(total_money.get('amount')),
                total_money_currency=total_money.get('currency', 'USD')
            ))
        
        return orders
    
    def parse_fulfillments(self) -> List[Order]:
        """Parse orders from orders.json"""
        if self._orders_data is None:
            self._orders_data = self._load_json(self.orders_path)
        
        fulfillments = []
        for order_data in self._orders_data.get('orders', []):
            # Parse fulfillments
            
            for ful_data in order_data.get('fulfillments', []):
                fulfillments.append(Fulfillment(
                    order_id=order_data.get('id', ''),
                    uid=ful_data.get('uid'),
                    type=ful_data.get('type'),
                    state=ful_data.get('state')
                ))

        
        return fulfillments
    
    def parse_order_details(self) -> List[OrderDetail]:
        """Parse order details (line items) from orders.json"""
        if self._orders_data is None:
            self._orders_data = self._load_json(self.orders_path)
        
        order_details = []
        for order_data in self._orders_data.get('orders', []):
            order_id = order_data.get('id', '')
            
            for line_item in order_data.get('line_items', []):
                gross_money = line_item.get('gross_sales_money', {})
                total_money = line_item.get('total_money', {})
                
                order_details.append(OrderDetail(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    itemvar_id=line_item.get('catalog_object_id', ''),
                    qty=int(line_item.get('quantity', 0)),
                    gross_amount_currency=gross_money.get('currency', 'USD'),
                    gross_amount=self._cents_to_dollars(gross_money.get('amount', 0)),
                    total_amount_currency=total_money.get('currency', 'USD'),
                    total_amount=self._cents_to_dollars(total_money.get('amount', 0))
                ))
        
        return order_details
    
    def parse_payments(self) -> List[Payment]:
        """Parse payments from payments.json"""
        if self._payments_data is None:
            self._payments_data = self._load_json(self.payments_path)
        
        payments = []
        for payment_data in self._payments_data.get('payments', []):
            # Parse money fields
            amount_money = payment_data.get('amount_money', {})
            tip_money = payment_data.get('tip_money', {})
            total_money = payment_data.get('total_money', {})
            
            payments.append(Payment(
                id=payment_data.get('id', ''),
                order_id=payment_data.get('order_id', ''),
                location_id=payment_data.get('location_id', ''),
                amount_currency=amount_money.get('currency', 'USD'),
                tip_amount_currency=tip_money.get('currency', 'USD'),
                total_money_currency=total_money.get('currency', 'USD'),
                created_at=self._parse_datetime(payment_data.get('created_at')),
                updated_at=self._parse_datetime(payment_data.get('updated_at')),
                amount=self._cents_to_dollars(amount_money.get('amount')),
                tip_amount=self._cents_to_dollars(tip_money.get('amount')),
                total_money=self._cents_to_dollars(total_money.get('amount')),
                source_type=payment_data.get('source_type'),
                status=payment_data.get('status')
            ))
        
        return payments
    
    def parse_card_details(self) -> List[CardDetails]:
        """Parse payments from payments.json"""
        if self._payments_data is None:
            self._payments_data = self._load_json(self.payments_path)
        
        card_details = []
        for payment_data in self._payments_data.get('payments', []):
            card_data = payment_data.get('card_details')
            if card_data:
                card_info = card_data.get('card', {})
                card_details.append(CardDetails(
                    payment_id=payment_data.get('id', ''),
                    status=card_data.get('status'),
                    card_brand=card_info.get('card_brand'),
                    last_4=card_info.get('last_4'),
                    exp_month=card_info.get('exp_month'),
                    exp_year=card_info.get('exp_year'),
                    entry_method=card_data.get('entry_method')
                ))
            
        
        return card_details

    def parse_cash_details(self) -> List[CashDetails]:
        """Parse payments from payments.json"""
        if self._payments_data is None:
            self._payments_data = self._load_json(self.payments_path)
        
        cash_details = []
        for payment_data in self._payments_data.get('payments', []):
            cash_data = payment_data.get('cash_details')
            if cash_data:
                buyer_money = cash_data.get('buyer_supplied_money', {})
                change_money = cash_data.get('change_back_money', {})
                cash_details.append(CashDetails(
                    payment_id=payment_data.get('id', ''),
                    buyer_supplied_currency=buyer_money.get('currency', 'USD'),
                    change_back_currency=change_money.get('currency', 'USD'),
                    buyer_supplied_money=self._cents_to_dollars(buyer_money.get('amount')),
                    change_back_money=self._cents_to_dollars(change_money.get('amount'))
                ))
        
        return cash_details
    
    def parse_all(self) -> Dict[str, List]:
        """
        Parse all Square data files and return unified models.
        
        Returns:
            Dictionary with keys: categories, items, item_variations, locations, orders, order_details, payments
        """
        return {
            'categories': self.parse_categories(),
            'items': self.parse_items(),
            'item_variations': self.parse_item_variations(),
            'locations': self.parse_locations(),
            'orders': self.parse_orders(),
            'order_details': self.parse_order_details(),
            'payments': self.parse_payments(),
            'item_loc_mapping': self.parse_item_loc_mappings(),
            'address': self.parse_address(),
            'fulfillments': self.parse_fulfillments(),
            'cash_details': self.parse_cash_details(),
            'card_details': self.parse_card_details()
        }


if __name__ == '__main__':
    # Example usage
    parser = SquareParser(
        catalog_path='data/sources/square/catalog.json',
        orders_path='data/sources/square/orders.json',
        payments_path='data/sources/square/payments.json',
        locations_path='data/sources/square/locations.json'
    )
    
    # Parse all data
    data = parser.parse_all()
    
    # Print summary
    print("\nSquare Data Parsed:")
    print(f"  Categories: {len(data['categories'])}")
    print(f"  Items: {len(data['items'])}")
    print(f"  Item Variations: {len(data['item_variations'])}")
    print(f"  Locations: {len(data['locations'])}")
    print(f"  Orders: {len(data['orders'])}")
    print(f"  Order Details: {len(data['order_details'])}")
    print(f"  Payments: {len(data['payments'])}")
    print(f"  Item_loc_mapping: {len(data['item_loc_mapping'])}")
    print(f"  Address: {len(data['address'])}")
    print(f"  Fullfilments: {len(data['fulfillments'])}")
    print(f"  Card: {len(data['card_details'])}")
    print(f"  Cash: {len(data['cash_details'])}")
    
    # Print first few examples
    import sys
    import io
    # Set UTF-8 encoding for stdout to handle emojis
    # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    if data['categories']:
        print(f"\nFirst Category: {data['categories'][0]}")
    if data['items']:
        print(f"First Item: {data['items'][0]}")
    if data['item_variations']:
        print(f"First Variation: {data['item_variations'][0]}")
    if data['locations']:
        print(f"First Location: {data['locations'][0]}")
    if data['orders']:
        print(f"First Order: {data['orders'][0]}")
    if data['order_details']:
        print(f"First Order Detail: {data['order_details'][0]}")
    if data['payments']:
        print(f"First Payment: {data['payments'][0]}")
    if data['item_loc_mapping']:
        print(f"First Item Loc Mapping: {data['item_loc_mapping'][0]}")
    if data['address']:
        print(f"First Address: {data['address'][0]}")
    if data['fulfillments']:
        print(f"First fulfillments: {data['fulfillments'][0]}")
    if data['card_details']:
        print(f"First Card details: {data['card_details'][0]}")
    if data['cash_details']:
        print(f"First Cash details: {data['cash_details'][0]}")
