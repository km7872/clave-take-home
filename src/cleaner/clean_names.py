#!/usr/bin/env python3
"""
Name cleaning script for items and item variations.

Groups similar names using fuzzy matching and GPT, then updates display_name fields.
Requires user confirmation before making database changes.
"""
import argparse
import sys
from typing import List, Dict, Any, Tuple
from collections import defaultdict

from src.db.dbConnect import db
from src.cleaner.fuzzy_grouper import group_similar_names, group_by_key
from src.cleaner.gpt_cleaner import GPTCleaner
from src.cleaner.db_updater import update_item_display_names, update_variation_display_names


def get_items_needing_cleaning() -> List[Dict[str, Any]]:
    """Fetch items that need display_name cleaned (where display_name IS NULL)."""
    try:
        # Fetch all items and filter for NULL display_name in Python
        # (Supabase Python client doesn't have a standard is_() method for NULL checks)
        response = db.table('items').select('id, name, category_id, display_name').execute()
        all_items = response.data if response.data else []
        # Filter for items where display_name is None or empty
        return [item for item in all_items if not item.get('display_name')]
    except Exception as e:
        print(f"Error fetching items: {str(e)}")
        return []


def get_variations_needing_cleaning() -> List[Dict[str, Any]]:
    """Fetch item variations that need display_name cleaned (where display_name IS NULL)."""
    try:
        # Fetch all variations and filter for NULL display_name in Python
        response = db.table('item_variations').select('id, name, item_id, display_name').execute()
        all_variations = response.data if response.data else []
        # Filter for variations where display_name is None or empty
        return [var for var in all_variations if not var.get('display_name')]
    except Exception as e:
        print(f"Error fetching item variations: {str(e)}")
        return []


def get_category_names() -> Dict[str, str]:
    """Fetch category ID to name mapping."""
    try:
        response = db.table('categories').select('id, name').execute()
        return {cat['id']: cat['name'] for cat in (response.data if response.data else [])}
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        return {}


def get_item_names() -> Dict[str, str]:
    """Fetch item ID to name mapping."""
    try:
        response = db.table('items').select('id, name').execute()
        return {item['id']: item['name'] for item in (response.data if response.data else [])}
    except Exception as e:
        print(f"Error fetching items: {str(e)}")
        return {}


def process_items(gpt_cleaner: GPTCleaner, category_names: Dict[str, str]) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
    """
    Process items: group by category, fuzzy match within categories, clean with GPT.
    
    Returns:
        Tuple of (updates list, preview data)
    """
    items = get_items_needing_cleaning()
    
    if not items:
        return [], []
    
    # Group by category_id
    items_by_category = group_by_key(items, 'category_id')
    
    updates = []
    preview_data = []
    
    for category_id, category_items in items_by_category.items():
        category_name = category_names.get(category_id, f"Category {category_id}")
        
        # Get unique names in this category
        unique_names = list(set(item['name'] for item in category_items))
        
        # Group similar names using fuzzy matching
        name_groups = group_similar_names(unique_names, threshold=75.0)

        # Filter groups that have 2 or more items (need cleaning due to variations)
        groups_needing_cleaning = [ng for ng in name_groups if len(ng) >= 2]
        
        # Call GPT cleaner once for all groups that need cleaning
        cleaned_names = []
        if groups_needing_cleaning:
            cleaned_names = gpt_cleaner.clean_item_names(groups_needing_cleaning, category_name)
        
        # Create a mapping from name_group (as sorted tuple for consistency) to cleaned_name
        name_group_to_cleaned = {}
        for i, name_group in enumerate(groups_needing_cleaning):
            # Use sorted tuple to ensure consistent matching regardless of order
            key = tuple(sorted(name_group))
            name_group_to_cleaned[key] = cleaned_names[i]
        
        # Process all name groups (both cleaned and single-item groups)
        for name_group in name_groups:
            # Use sorted tuple for consistent lookup
            group_key = tuple(sorted(name_group))
            if group_key in name_group_to_cleaned:
                # Use GPT-cleaned name for groups with variations
                cleaned_name = name_group_to_cleaned[group_key]
            else:
                # For single-item groups, use the name as-is
                cleaned_name = name_group[0]
            
            # Create preview entry
            group_preview = {
                'category': category_name,
                'original_names': name_group,
                'cleaned_name': cleaned_name
            }
            preview_data.append(group_preview)
            
            # Create updates for all items with these names in this category
            for item in category_items:
                if item['name'] in name_group:
                    updates.append({
                        'id': item['id'],
                        'display_name': cleaned_name
                    })
        
        # for name_group in name_groups:
        #     # Use GPT to clean (works for single items too - standardizes capitalization, etc.)
        #     # cleaned_name = gpt_cleaner.clean_item_names(name_group, category_name)
        #     print(name_group)
            
            # Create preview entry
            # group_preview = {
            #     'category': category_name,
            #     'original_names': name_group,
            #     'cleaned_name': cleaned_name
            # }
            # preview_data.append(group_preview)
            
            # # Create updates for all items with these names in this category
            # for item in category_items:
            #     if item['name'] in name_group:
            #         updates.append({
            #             'id': item['id'],
            #             'display_name': cleaned_name
            #         })
    
    return updates, preview_data


def process_variations(gpt_cleaner: GPTCleaner, item_names: Dict[str, str]) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
    """
    Process item variations: group by item_id, clean variation names with GPT.
    
    Returns:
        Tuple of (updates list, preview data)
    """
    variations = get_variations_needing_cleaning()
    
    if not variations:
        return [], []
    
    # Group by item_id
    variations_by_item = group_by_key(variations, 'item_id')
    
    updates = []
    preview_data = []
    
    # Prepare all variation groups for batch processing
    variation_groups = []
    item_ids_order = []
    
    for item_id, item_variations in variations_by_item.items():
        item_name = item_names.get(item_id, f"Item {item_id}")
        # Get unique variation names for this item
        unique_names = list(set(var['name'] for var in item_variations))
        
        if unique_names:  # Only add if there are variation names
            variation_groups.append((unique_names, item_name))
            item_ids_order.append(item_id)
    
    # Call GPT cleaner once for all variation groups
    cleaned_mappings = []
    if variation_groups:
        cleaned_mappings = gpt_cleaner.clean_variation_names(variation_groups)
    
    # Process results and create updates/previews
    for i, item_id in enumerate(item_ids_order):
        item_variations = variations_by_item[item_id]
        item_name = item_names.get(item_id, f"Item {item_id}")
        unique_names = list(set(var['name'] for var in item_variations))
        cleaned_mapping = cleaned_mappings[i] if i < len(cleaned_mappings) else {}
        
        # Create preview entry
        group_preview = {
            'item_name': item_name,
            'variations': [
                {'original': name, 'cleaned': cleaned_mapping.get(name, name)}
                for name in unique_names
            ]
        }
        preview_data.append(group_preview)
        
        # Create updates for all variations
        for variation in item_variations:
            original_name = variation['name']
            cleaned_name = cleaned_mapping.get(original_name, original_name)
            
            updates.append({
                'id': variation['id'],
                'display_name': cleaned_name
            })
    
    return updates, preview_data


def print_preview(item_previews: List[Dict], variation_previews: List[Dict]):
    """Print preview of changes to be made."""
    print("\n" + "=" * 80)
    print("NAME CLEANING PREVIEW")
    print("=" * 80)
    
    if item_previews:
        print("\nITEMS:")
        print("-" * 80)
        for preview in item_previews:
            print(f"\nCategory: {preview['category']}")
            for name in preview['original_names']:
                change_indicator = "" if name == preview['cleaned_name'] else " →"
                print(f'  "{name}"{change_indicator} display_name: "{preview["cleaned_name"]}"')
    
    if variation_previews:
        print("\nITEM VARIATIONS:")
        print("-" * 80)
        for preview in variation_previews:
            print(f"\nItem: {preview['item_name']}")
            for var in preview['variations']:
                change_indicator = "" if var['original'] == var['cleaned'] else " →"
                print(f'  "{var["original"]}"{change_indicator} display_name: "{var["cleaned"]}"')
    
    total_items = sum(len(p['original_names']) for p in item_previews)
    total_variations = sum(len(p['variations']) for p in variation_previews)
    
    print("\n" + "-" * 80)
    print(f"Total items to update: {total_items}")
    print(f"Total variations to update: {total_variations}")
    print("=" * 80)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Clean item and variation names using GPT')
    parser.add_argument('--table', choices=['items', 'item_variations', 'both'], default='both',
                        help='Which table to clean (default: both)')
    args = parser.parse_args()
    
    print("Starting name cleaning process...")
    print(f"Processing: {args.table}")
    
    # Initialize GPT cleaner
    try:
        gpt_cleaner = GPTCleaner()
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Make sure OPENAI_API_KEY is set in your environment variables.")
        sys.exit(1)
    
    item_updates = []
    variation_updates = []
    item_previews = []
    variation_previews = []
    
    # Process items if requested
    if args.table in ['items', 'both']:
        print("\nProcessing items...")
        category_names = get_category_names()
        item_updates, item_previews = process_items(gpt_cleaner, category_names)
        print(f"Found {len(item_updates)} items to update")
    
    # Process variations if requested
    if args.table in ['item_variations', 'both']:
        print("\nProcessing item variations...")
        item_names = get_item_names()
        variation_updates, variation_previews = process_variations(gpt_cleaner, item_names)
        print(f"Found {len(variation_updates)} variations to update")
    
    # Show preview
    if item_previews or variation_previews:
        print_preview(item_previews, variation_previews)
        
        # Get confirmation
        print("\nProceed with updating display_name fields? (yes/no): ", end='')
        confirmation = input().strip().lower()
        
        if confirmation in ['yes', 'y']:
            print("\nUpdating database...")
            
            updated_items = 0
            updated_variations = 0
            items_success = True
            variations_success = True
            
            try:
                if item_updates:
                    updated_items, items_success = update_item_display_names(item_updates)
                    if items_success:
                        print(f"Updated {updated_items} items")
                    else:
                        print(f"Failed to update items. Rolled back changes.")
                
                if variation_updates and items_success:
                    updated_variations, variations_success = update_variation_display_names(variation_updates)
                    if variations_success:
                        print(f"Updated {updated_variations} variations")
                    else:
                        print(f"Failed to update variations. Rolled back changes.")
                
                if items_success and variations_success:
                    print(f"\nDone! Updated {updated_items} items and {updated_variations} variations.")
                else:
                    print(f"\nError: Some updates failed. Changes have been rolled back.")
            except Exception as e:
                print(f"\nError during database update: {str(e)}")
                print("All changes have been rolled back.")
        else:
            print("\nCancelled. No changes made to the database.")
    else:
        print("\nNo items or variations found that need cleaning (all display_name fields are already set).")


if __name__ == '__main__':
    main()

