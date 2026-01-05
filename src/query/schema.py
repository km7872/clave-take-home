"""
Database schema definition for query building.
Contains table and column information used by the LLM to generate queries.
"""
from typing import Dict, List


# Database schema definition
# Maps to the actual Supabase tables
DATABASE_SCHEMA = {
    "locations": {
        "columns": ["id", "name", "timezone", "status", "type", "merchant_id", "created_at", "updated_at"],
        "description": "Restaurant locations (Downtown, Airport, Mall, University)",
        "relationships": {},
        "primary_key": "id"
    },
    "addresses": {
        "columns": ["id", "location_id", "address_line_1", "locality", "administrative_district_level_1", "postal_code", "country", "created_at", "updated_at"],
        "description": "Address information for locations",
        "relationships": {"location_id": "locations.id"},
        "primary_key": "id"
    },
    "categories": {
        "columns": ["id", "name", "display_name", "created_at", "updated_at"],
        "description": "Product categories (e.g., Burgers, Sides, Drinks)",
        "relationships": {},
        "primary_key": "id"
    },
    "items": {
        "columns": ["id", "name", "description", "display_name", "category_id", "created_at", "updated_at"],
        "description": "Menu items/products",
        "relationships": {"category_id": "categories.id"},
        "primary_key": "id"
    },
    "item_variations": {
        "columns": ["id", "item_id", "name", "price", "price_currency", "display_name", "created_at", "updated_at"],
        "description": "Variations of items (e.g., sizes, options)",
        "relationships": {"item_id": "items.id"},
        "primary_key": "id"
    },
    "item_location_mapping": {
        "columns": ["id", "item_id", "location_id", "created_at", "updated_at"],
        "description": "Mapping of which items are available at which locations",
        "relationships": {"item_id": "items.id", "location_id": "locations.id"},
        "primary_key": "id"
    },
    "orders": {
        "columns": ["id", "location_id", "ref_id", "source", "created_at", "updated_at", "closed_at", 
                   "tip_amount", "tip_amount_currency", "tax_amount", "tax_currency", 
                   "total_money", "total_money_currency"],
        "description": "Order records with revenue, tips, and taxes",
        "relationships": {"location_id": "locations.id"},
        "primary_key": "id"
    },
    "order_details": {
        "columns": ["id", "order_id", "itemvar_id", "qty", "gross_amount", "gross_amount_currency", 
                   "total_amount", "total_amount_currency", "created_at", "updated_at"],
        "description": "Line items in orders (what was ordered, quantities, prices)",
        "relationships": {"order_id": "orders.id", "itemvar_id": "item_variations.id"},
        "primary_key": "id"
    },
    "fulfillments": {
        "columns": ["id", "order_id", "uid", "type", "state", "created_at", "updated_at"],
        "description": "Order fulfillment information (DINE_IN, PICKUP, DELIVERY)",
        "relationships": {"order_id": "orders.id"},
        "primary_key": "id"
    },
    "payments": {
        "columns": ["id", "order_id", "location_id", "amount", "amount_currency", "tip_amount", 
                   "tip_amount_currency", "total_money", "total_money_currency", "source_type", 
                   "status", "created_at", "updated_at"],
        "description": "Payment records (CARD, CASH, etc.)",
        "relationships": {"order_id": "orders.id", "location_id": "locations.id"},
        "primary_key": "id"
    },
    "card_details": {
        "columns": ["id", "payment_id", "status", "card_brand", "last_4", "exp_month", "exp_year", 
                   "entry_method", "created_at", "updated_at"],
        "description": "Credit card payment details",
        "relationships": {"payment_id": "payments.id"},
        "primary_key": "id"
    },
    "cash_details": {
        "columns": ["id", "payment_id", "buyer_supplied_currency", "change_back_currency", 
                   "buyer_supplied_money", "change_back_money", "created_at", "updated_at"],
        "description": "Cash payment details",
        "relationships": {"payment_id": "payments.id"},
        "primary_key": "id"
    }
}


def get_schema_summary() -> str:
    """
    Get a formatted string of the schema for LLM prompts.
    
    Returns:
        Formatted string describing all tables and columns
    """
    lines = ["Database Schema:"]
    lines.append("=" * 80)
    
    for table_name, table_info in DATABASE_SCHEMA.items():
        lines.append(f"\nTable: {table_name}")
        lines.append(f"  Description: {table_info['description']}")
        lines.append(f"  Columns: {', '.join(table_info['columns'])}")
        if table_info['relationships']:
            rels = [f"{fk} -> {ref}" for fk, ref in table_info['relationships'].items()]
            lines.append(f"  Relationships: {', '.join(rels)}")
    
    return "\n".join(lines)


def get_schema_json() -> Dict:
    """
    Get schema as JSON for LLM consumption.
    
    Returns:
        Dictionary representation of schema
    """
    return DATABASE_SCHEMA


def validate_table(table_name: str) -> bool:
    """Check if table exists in schema"""
    return table_name in DATABASE_SCHEMA


def validate_column(table_name: str, column_name: str) -> bool:
    """Check if column exists in table"""
    if not validate_table(table_name):
        return False
    return column_name in DATABASE_SCHEMA[table_name]["columns"]

