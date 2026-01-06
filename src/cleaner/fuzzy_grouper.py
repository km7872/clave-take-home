"""
Fuzzy matching module for grouping similar names.
Uses rapidfuzz for token-based similarity matching.
"""
from typing import List, Dict, Set
from rapidfuzz import fuzz, process
from collections import defaultdict


def group_similar_names(names: List[str], threshold: float = 75.0) -> List[List[str]]:
    """
    Group similar names using token-based fuzzy matching.
    
    Args:
        names: List of unique names to group
        threshold: Similarity threshold (0-100) for grouping
        
    Returns:
        List of groups, where each group is a list of similar names
    """
    if not names:
        return []
    
    # Use token sort ratio - good for handling word order differences
    # and handles variations like "Hash Browns" vs "Hashbrowns"
    groups = []
    used = set()
    
    for name in names:
        if name in used:
            continue
        
        # Find all similar names
        group = [name]
        used.add(name)
        
        for other_name in names:
            if other_name in used or other_name == name:
                continue
            
            # Use token_sort_ratio for better matching of names with same words in different order
            similarity = fuzz.token_sort_ratio(name.lower(), other_name.lower())
            
            if similarity >= threshold:
                group.append(other_name)
                used.add(other_name)
        
        if group:
            groups.append(group)
    
    return groups


def group_by_key(items: List[Dict], key_field: str) -> Dict[str, List[Dict]]:
    """
    Group items by a key field (e.g., category_id or item_id).
    
    Args:
        items: List of dictionaries to group
        key_field: Field name to group by
        
    Returns:
        Dictionary mapping key values to lists of items
    """
    grouped = defaultdict(list)
    
    for item in items:
        key_value = item.get(key_field)
        if key_value:
            grouped[key_value].append(item)
    
    return dict(grouped)

