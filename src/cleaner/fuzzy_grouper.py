"""
Fuzzy matching module for grouping similar names.
Uses rapidfuzz for token-based similarity matching.
"""
import re
from typing import List, Dict, Set
from rapidfuzz import fuzz, process
from collections import defaultdict


def normalize_for_matching(name: str) -> str:
    """
    Normalize name for better fuzzy matching.
    Removes quantities, extra spaces, and normalizes common patterns.
    
    Args:
        name: Original name
        
    Returns:
        Normalized name
    """
    # Convert to lowercase
    normalized = name.lower().strip()
    
    # Remove quantities (e.g., "12pc", "6pc", "12 pcs", etc.)
    normalized = re.sub(r'\d+\s*(pc|pcs|piece|pieces|p)\b', '', normalized, flags=re.IGNORECASE)
    
    # Remove extra whitespace and normalize hyphens
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = re.sub(r'\s*-\s*', ' ', normalized)  # Normalize hyphens to spaces
    
    # Remove leading/trailing spaces
    normalized = normalized.strip()
    
    return normalized


def group_similar_names(names: List[str], threshold: float = 75.0) -> List[List[str]]:
    """
    Group similar names using multiple fuzzy matching strategies.
    
    Args:
        names: List of unique names to group
        threshold: Similarity threshold (0-100) for grouping
        
    Returns:
        List of groups, where each group is a list of similar names
    """
    if not names:
        return []
    
    groups = []
    used = set()
    
    for name in names:
        if name in used:
            continue
        
        # Find all similar names
        group = [name]
        used.add(name)
        
        name_lower = name.lower()
        name_normalized = normalize_for_matching(name)
        
        for other_name in names:
            if other_name in used or other_name == name:
                continue
            
            other_lower = other_name.lower()
            other_normalized = normalize_for_matching(other_name)
            
            # Try multiple similarity metrics and take the best
            # token_sort_ratio: handles word order differences
            token_sort = fuzz.token_sort_ratio(name_lower, other_lower)
            token_sort_norm = fuzz.token_sort_ratio(name_normalized, other_normalized)
            
            # token_set_ratio: better for subsets (e.g., "Hash Browns" vs "Hashbrowns")
            token_set = fuzz.token_set_ratio(name_lower, other_lower)
            token_set_norm = fuzz.token_set_ratio(name_normalized, other_normalized)
            
            # partial_ratio: checks if one string is contained in another
            # Useful for "Buffalo Wings" vs "Buffalo Wings 12pc"
            partial = fuzz.partial_ratio(name_lower, other_lower)
            partial_norm = fuzz.partial_ratio(name_normalized, other_normalized)
            
            # WRatio: weighted ratio combining multiple methods
            weighted = fuzz.WRatio(name_lower, other_lower)
            weighted_norm = fuzz.WRatio(name_normalized, other_normalized)
            
            # Special case: if normalized versions are very similar, they should match
            # This handles "Hash Browns" vs "Hashbrowns" better
            if name_normalized and other_normalized:
                # Check if normalized strings are very similar (lower threshold for normalized)
                if fuzz.ratio(name_normalized, other_normalized) >= max(threshold - 10, 60):
                    similarity = 100  # Force match if normalized versions are very close
                else:
                    # Use the maximum similarity score from all methods
                    similarity = max(token_sort, token_sort_norm, token_set, token_set_norm, 
                                   partial, partial_norm, weighted, weighted_norm)
            else:
                # Use the maximum similarity score from all methods
                similarity = max(token_sort, token_sort_norm, token_set, token_set_norm, 
                               partial, partial_norm, weighted, weighted_norm)
            
            # Special handling for cases where one name contains the other
            # e.g., "Buffalo Wings" should match "Buffalo Wings 12pc"
            if name_normalized in other_normalized or other_normalized in name_normalized:
                if name_normalized and other_normalized and len(name_normalized) > 3 and len(other_normalized) > 3:
                    # If one is a substring of the other and both are substantial, match them
                    shorter = min(len(name_normalized), len(other_normalized))
                    longer = max(len(name_normalized), len(other_normalized))
                    if shorter / longer >= 0.7:  # At least 70% overlap
                        similarity = max(similarity, 85)  # Boost similarity
            
            # Special handling: if names share a significant common word (3+ chars), boost similarity
            # This helps match "Fries - Large" with "French Fries" or "Wings 12pc" with "Buffalo Wings"
            name_words = set(name_normalized.split())
            other_words = set(other_normalized.split())
            common_words = name_words.intersection(other_words)
            
            # Find significant common words (length >= 3)
            significant_common = [w for w in common_words if len(w) >= 3]
            if significant_common:
                # If they share a significant word and the difference is just modifiers, boost similarity
                name_only = name_words - other_words
                other_only = other_words - name_words
                # Common modifier words that shouldn't prevent matching
                modifiers = {'large', 'lg', 'small', 'sm', 'medium', 'md', 'regular', 'reg', 
                           'extra', 'xl', 'xxl', 'single', 'double', 'dbl'}
                
                # If the only differences are modifiers or short words, boost similarity
                name_diff = {w for w in name_only if len(w) >= 3 and w not in modifiers}
                other_diff = {w for w in other_only if len(w) >= 3 and w not in modifiers}
                
                # Case 1: One side only has modifiers/short words
                if not name_diff or not other_diff:
                    similarity = max(similarity, 80)  # Boost similarity
                # Case 2: If one name is just the common word + modifiers, and other has descriptive words
                # e.g., "fries large" vs "french fries" - both have "fries", one has "large" (modifier),
                # other has "french" (descriptive). If the common word is the main noun, they should match.
                elif len(significant_common) >= 1 and len(name_words) <= 3 and len(other_words) <= 3:
                    # If both are short phrases and share a significant word, they're likely the same item
                    # with different descriptions (e.g., "Fries Large" = "Large French Fries")
                    if max(len(name_diff), len(other_diff)) <= 1:  # At most one different significant word
                        similarity = max(similarity, 75)  # Boost to threshold level
            
            if similarity >= threshold:
                group.append(other_name)
                used.add(other_name)
        
        if group:
            groups.append(group)
    
    # Post-process: merge groups that have overlapping names
    # This handles transitive relationships (A matches B, B matches C, so A/B/C should be together)
    if not groups:
        return []
    
    merged_groups = []
    
    for group in groups:
        current_group = set(group)
        merged = False
        
        # Check if this group overlaps with any already merged group
        for merged_group in merged_groups:
            if current_group.intersection(merged_group):
                # Merge the groups
                merged_group.update(current_group)
                merged = True
                break
        
        if not merged:
            merged_groups.append(current_group)
    
    # Convert sets back to lists
    return [list(group) for group in merged_groups]


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

