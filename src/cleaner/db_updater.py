"""
Database update module for display_name fields.
Uses transaction-like pattern for rollback support.
"""
from typing import List, Dict, Tuple
from src.db.dbConnect import db


def update_item_display_names(updates: List[Dict[str, str]]) -> Tuple[int, bool]:
    """
    Update display_name for items with rollback support.
    Tracks updated IDs and sets them back to NULL on error.
    
    Args:
        updates: List of dicts with 'id' and 'display_name' keys
        
    Returns:
        Tuple of (number of records updated, success boolean)
    """
    if not updates:
        return 0, True
    
    updated_count = 0
    updated_ids = []
    
    try:
        for update in updates:
            db.table('items').update({
                'display_name': update['display_name']
            }).eq('id', update['id']).execute()
            updated_ids.append(update['id'])
            updated_count += 1
        
        return updated_count, True
        
    except Exception as e:
        # Rollback: set all updated IDs back to NULL (since they were NULL before)
        print(f"\nError during item updates. Rolling back {len(updated_ids)} updates...")
        print(f"Error: {str(e)}")
        
        for item_id in updated_ids:
            try:
                db.table('items').update({
                    'display_name': None
                }).eq('id', item_id).execute()
            except Exception as rollback_error:
                print(f"Warning: Error rolling back item {item_id}: {str(rollback_error)}")
        
        return updated_count, False


def update_variation_display_names(updates: List[Dict[str, str]]) -> Tuple[int, bool]:
    """
    Update display_name for item variations with rollback support.
    Tracks updated IDs and sets them back to NULL on error.
    
    Args:
        updates: List of dicts with 'id' and 'display_name' keys
        
    Returns:
        Tuple of (number of records updated, success boolean)
    """
    if not updates:
        return 0, True
    
    updated_count = 0
    updated_ids = []
    
    try:
        for update in updates:
            db.table('item_variations').update({
                'display_name': update['display_name']
            }).eq('id', update['id']).execute()
            updated_ids.append(update['id'])
            updated_count += 1
        
        return updated_count, True
        
    except Exception as e:
        # Rollback: set all updated IDs back to NULL (since they were NULL before)
        print(f"\nError during variation updates. Rolling back {len(updated_ids)} updates...")
        print(f"Error: {str(e)}")
        
        for var_id in updated_ids:
            try:
                db.table('item_variations').update({
                    'display_name': None
                }).eq('id', var_id).execute()
            except Exception as rollback_error:
                print(f"Warning: Error rolling back variation {var_id}: {str(rollback_error)}")
        
        return updated_count, False

