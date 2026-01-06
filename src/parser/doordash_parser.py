"""
Parser for DoorDash orders JSON data file.
Maps DoorDash data structure to existing unified models.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid

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


class DoorDashParser:
    """Parser for DoorDash orders JSON file."""

    def __init__(self, orders_path: str):
        """
        Initialize parser with path to DoorDash orders JSON file.

        Args:
            orders_path: Path to doordash_orders.json
        """
        self.orders_path = orders_path
        self._data: Optional[Dict] = None

    def _load_json(self) -> Dict:
        """Load JSON file."""
        if self._data is None:
            with open(self.orders_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        return self._data

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    def _cents_to_dollars(self, cents: Optional[int]) -> Optional[float]:
        """Convert amount from cents to dollars."""
        if cents is None:
            return None
        return cents / 100.0

    # -------------------- Dimension-like entities -------------------- #

    def parse_locations(self) -> List[Location]:
        """Parse locations (stores) from DoorDash JSON."""
        data = self._load_json()
        merchant_id = data.get("merchant", {}).get("merchant_id")

        locations: List[Location] = []
        for store in data.get("stores", []):
            locations.append(
                Location(
                    id=store.get("store_id", ""),
                    name=store.get("name", ""),
                    timezone=store.get("timezone"),
                    status=None,
                    type="DOORDASH_STORE",
                    merchant_id=merchant_id,
                )
            )

        return locations

    def parse_addresses(self) -> List[Address]:
        """Parse store addresses from DoorDash JSON into Address models."""
        data = self._load_json()

        addresses: List[Address] = []
        for store in data.get("stores", []):
            addr = store.get("address", {}) or {}
            addresses.append(
                Address(
                    location_id=store.get("store_id", ""),
                    address_line_1=addr.get("street"),
                    locality=addr.get("city"),
                    administrative_district_level_1=addr.get("state"),
                    postal_code=addr.get("zip_code"),
                    country=addr.get("country"),
                )
            )

        return addresses

    def parse_categories_items_and_variations(
        self,
    ) -> Dict[str, List]:
        """
        Parse categories, items, and item variations from order_items.

        DoorDash does not provide a separate catalog file, so we reconstruct
        categories and items from observed order_items across all orders.

        Returns:
            Dict with keys: categories, items, item_variations
        """
        data = self._load_json()

        # Collect unique categories and items keyed by their natural IDs/names
        category_by_name: Dict[str, Category] = {}
        item_by_id: Dict[str, Item] = {}
        variation_by_id: Dict[str, ItemVariation] = {}

        merchant_currency = data.get("merchant", {}).get("currency", "USD")

        for order in data.get("orders", []):
            for line in order.get("order_items", []):
                raw_category_name = line.get("category")
                if raw_category_name:
                    if raw_category_name not in category_by_name:
                        # Use the raw category string as ID to keep it stable
                        category_by_name[raw_category_name] = Category(
                            id=raw_category_name,
                            name=raw_category_name,
                            display_name=None,
                        )

                item_id = line.get("item_id")
                if not item_id:
                    continue

                # Create Item if not seen before
                if item_id not in item_by_id:
                    item_by_id[item_id] = Item(
                        id=item_id,
                        name=line.get("name", ""),
                        description=None,
                        category_id=raw_category_name,
                        display_name=None,
                    )

                # Create a simple ItemVariation per item, using item_id as variation id
                if item_id not in variation_by_id:
                    variation_by_id[item_id] = ItemVariation(
                        id=item_id,
                        item_id=item_id,
                        name=line.get("name", ""),
                        price_currency=merchant_currency,
                        price=self._cents_to_dollars(line.get("unit_price", 0)),
                        display_name=None,
                    )

        return {
            "categories": list(category_by_name.values()),
            "items": list(item_by_id.values()),
            "item_variations": list(variation_by_id.values()),
        }

    def parse_item_location_mappings(self) -> List[ItemLocMapping]:
        """Infer item-location mappings from which items are sold at which stores."""
        data = self._load_json()

        seen_pairs = set()
        mappings: List[ItemLocMapping] = []

        for order in data.get("orders", []):
            store_id = order.get("store_id")
            if not store_id:
                continue
            for line in order.get("order_items", []):
                item_id = line.get("item_id")
                if not item_id:
                    continue
                key = (item_id, store_id)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                mappings.append(
                    ItemLocMapping(
                        item_id=item_id,
                        location_id=store_id,
                    )
                )

        return mappings

    # -------------------- Fact-like entities -------------------- #

    def parse_orders(self) -> List[Order]:
        """Parse orders into Order models."""
        data = self._load_json()
        currency = data.get("merchant", {}).get("currency", "USD")

        orders: List[Order] = []
        for order in data.get("orders", []):
            orders.append(
                Order(
                    id=order.get("external_delivery_id", ""),
                    location_id=order.get("store_id", ""),
                    ref_id=order.get("external_delivery_id"),
                    source="DoorDash",
                    created_at=self._parse_datetime(order.get("created_at")),
                    updated_at=self._parse_datetime(
                        order.get("delivery_time") or order.get("pickup_time")
                    ),
                    closed_at=self._parse_datetime(order.get("delivery_time")),
                    tip_amount=self._cents_to_dollars(order.get("dasher_tip")),
                    tip_amount_currency=currency,
                    tax_amount=self._cents_to_dollars(order.get("tax_amount")),
                    tax_currency=currency,
                    # Use total charged to consumer to align with "customer total" semantics
                    total_money=self._cents_to_dollars(
                        order.get("total_charged_to_consumer")
                    ),
                    total_money_currency=currency,
                )
            )

        return orders

    def parse_fulfillments(self) -> List[Fulfillment]:
        """Parse fulfillment info from orders into Fulfillment models."""
        data = self._load_json()

        fulfillments: List[Fulfillment] = []
        for order in data.get("orders", []):
            fulfillments.append(
                Fulfillment(
                    order_id=order.get("external_delivery_id", ""),
                    uid=None,
                    type=order.get("order_fulfillment_method"),
                    state=order.get("order_status"),
                )
            )

        return fulfillments

    def parse_order_details(self) -> List[OrderDetail]:
        """Parse order line items into OrderDetail models."""
        data = self._load_json()
        currency = data.get("merchant", {}).get("currency", "USD")

        details: List[OrderDetail] = []
        for order in data.get("orders", []):
            order_id = order.get("external_delivery_id", "")
            for line in order.get("order_items", []):
                details.append(
                    OrderDetail(
                        id=str(uuid.uuid4()),
                        order_id=order_id,
                        itemvar_id=line.get("item_id", ""),
                        qty=int(line.get("quantity", 0)),
                        gross_amount_currency=currency,
                        gross_amount=self._cents_to_dollars(line.get("unit_price", 0)),
                        total_amount_currency=currency,
                        total_amount=self._cents_to_dollars(
                            line.get("total_price", 0)
                        ),
                    )
                )

        return details

    def parse_payments(self) -> List[Payment]:
        """
        Parse simplified payment info per order into Payment models.

        DoorDash does not expose card/cash breakdown for the merchant side;
        we treat each order as a single payout/payment record.
        """
        data = self._load_json()
        currency = data.get("merchant", {}).get("currency", "USD")

        payments: List[Payment] = []
        for order in data.get("orders", []):
            payments.append(
                Payment(
                    id=order.get("external_delivery_id", ""),
                    order_id=order.get("external_delivery_id", ""),
                    location_id=order.get("store_id", ""),
                    amount_currency=currency,
                    tip_amount_currency=currency,
                    total_money_currency=currency,
                    created_at=self._parse_datetime(order.get("created_at")),
                    updated_at=self._parse_datetime(order.get("delivery_time")),
                    # Amount received by merchant
                    amount=self._cents_to_dollars(order.get("merchant_payout")),
                    tip_amount=self._cents_to_dollars(order.get("dasher_tip")),
                    total_money=self._cents_to_dollars(
                        order.get("total_charged_to_consumer")
                    ),
                    source_type="DOORDASH_PAYOUT",
                    status=order.get("order_status"),
                )
            )

        return payments

    # -------------------- Convenience -------------------- #

    def parse_all(self) -> Dict[str, List]:
        """
        Parse all DoorDash data into unified models.

        Returns:
            Dictionary with keys: categories, items, item_variations, locations,
            orders, order_details, payments, item_loc_mapping, address, fulfillments.
            (cash_details and card_details are not applicable for DoorDash and
            are returned as empty lists for compatibility.)
        """
        catalog_parts = self.parse_categories_items_and_variations()

        return {
            "categories": catalog_parts["categories"],
            "items": catalog_parts["items"],
            "item_variations": catalog_parts["item_variations"],
            "locations": self.parse_locations(),
            "orders": self.parse_orders(),
            "order_details": self.parse_order_details(),
            "payments": self.parse_payments(),
            "item_loc_mapping": self.parse_item_location_mappings(),
            "address": self.parse_addresses(),
            "fulfillments": self.parse_fulfillments(),
            # Not applicable for DoorDash, but keep keys for downstream code
            "cash_details": [],
            "card_details": [],
        }


if __name__ == "__main__":
    # Simple debug usage
    parser = DoorDashParser(orders_path="data/sources/doordash_orders.json")
    data = parser.parse_all()

    print("\nDoorDash Data Parsed:")
    print(f"  Locations: {len(data['locations'])}")
    print(f"  Addresses: {len(data['address'])}")
    print(f"  Categories: {len(data['categories'])}")
    print(f"  Items: {len(data['items'])}")
    print(f"  Item Variations: {len(data['item_variations'])}")
    print(f"  Item-Location Mappings: {len(data['item_loc_mapping'])}")
    print(f"  Orders: {len(data['orders'])}")
    print(f"  Order Details: {len(data['order_details'])}")
    print(f"  Fulfillments: {len(data['fulfillments'])}")
    print(f"  Payments: {len(data['payments'])}")


