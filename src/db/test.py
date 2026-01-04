from src.parser.square_parser import SquareParser
from src.db.insert import (
    insert_locations, insert_addresses, insert_categories, insert_items,
    insert_item_variations, insert_item_location_mapping, insert_orders,
    insert_order_details, insert_fulfillments, insert_payments,
    insert_card_details, insert_cash_details
)
from src.db.get_data import get_data
from src.db.transaction import begin_transaction, commit_transaction, rollback_transaction

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
    
    # Begin transaction
    txn = begin_transaction()
    print("Transaction started...")
    
    try:
        # Insert all data in proper order (respecting foreign key constraints)
        print("\nInserting data into Supabase...")
        
        # 1. Locations (no dependencies)
        print("\n1. Inserting locations...")
        response, status = txn.execute_insert('locations', insert_locations, data['locations'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert locations: {response.get('error', 'Unknown error')}")
        
        # 2. Addresses (depends on locations)
        print("\n2. Inserting addresses...")
        response, status = txn.execute_insert('addresses', insert_addresses, data['address'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert addresses: {response.get('error', 'Unknown error')}")
        
        # 3. Categories (no dependencies)
        print("\n3. Inserting categories...")
        response, status = txn.execute_insert('categories', insert_categories, data['categories'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert categories: {response.get('error', 'Unknown error')}")
        
        # 4. Items (depends on categories)
        print("\n4. Inserting items...")
        response, status = txn.execute_insert('items', insert_items, data['items'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert items: {response.get('error', 'Unknown error')}")
        
        # 5. Item variations (depends on items)
        print("\n5. Inserting item variations...")
        response, status = txn.execute_insert('item_variations', insert_item_variations, data['item_variations'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert item variations: {response.get('error', 'Unknown error')}")
        
        # 6. Item location mapping (depends on items and locations)
        print("\n6. Inserting item location mappings...")
        response, status = txn.execute_insert('item_location_mapping', insert_item_location_mapping, data['item_loc_mapping'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert item location mappings: {response.get('error', 'Unknown error')}")
        
        # 7. Orders (depends on locations)
        print("\n7. Inserting orders...")
        response, status = txn.execute_insert('orders', insert_orders, data['orders'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert orders: {response.get('error', 'Unknown error')}")
        
        # 8. Order details (depends on orders and item_variations)
        print("\n8. Inserting order details...")
        response, status = txn.execute_insert('order_details', insert_order_details, data['order_details'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert order details: {response.get('error', 'Unknown error')}")
        
        # 9. Fulfillments (depends on orders)
        print("\n9. Inserting fulfillments...")
        response, status = txn.execute_insert('fulfillments', insert_fulfillments, data['fulfillments'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert fulfillments: {response.get('error', 'Unknown error')}")
        
        # 10. Payments (depends on orders and locations)
        print("\n10. Inserting payments...")
        response, status = txn.execute_insert('payments', insert_payments, data['payments'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert payments: {response.get('error', 'Unknown error')}")
        
        # 11. Card details (depends on payments)
        print("\n11. Inserting card details...")
        response, status = txn.execute_insert('card_details', insert_card_details, data['card_details'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert card details: {response.get('error', 'Unknown error')}")
        
        # 12. Cash details (depends on payments)
        print("\n12. Inserting cash details...")
        response, status = txn.execute_insert('cash_details', insert_cash_details, data['cash_details'])
        print(f"   Status: {status}, Count: {response.get('count', 0)}")
        if status != 200:
            raise Exception(f"Failed to insert cash details: {response.get('error', 'Unknown error')}")
        
        # Commit transaction if all inserts succeeded
        commit_transaction()
        print("\nTransaction committed successfully!")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Rolling back transaction...")
        rollback_success = rollback_transaction()
        if rollback_success:
            print("Transaction rolled back successfully")
        else:
            print("Warning: Some records may not have been rolled back")
        raise
    
    # Get data from each table
    print("\n\nRetrieving data from each table...")
    tables = [
        'locations', 'addresses', 'categories', 'items', 'item_variations',
        'item_location_mapping', 'orders', 'order_details', 'fulfillments',
        'payments', 'card_details', 'cash_details'
    ]
    
    for table in tables:
        print(f"\n{table}:")
        result = get_data(table)
        if result and hasattr(result, 'data'):
            print(f"  Count: {len(result.data)}")
            if result.data:
                print(f"  First record: {result.data[0]}")
        else:
            print(f"  Result: {result}")
