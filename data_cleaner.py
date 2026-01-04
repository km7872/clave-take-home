"""
Data cleaning and normalization utilities for Square data.
Analyzes parsed data and identifies inconsistencies, typos, duplicates, etc.
"""
from typing import List, Dict, Set
from collections import defaultdict, Counter
from src.dataclasses import (
    Category, Item, ItemVariation, Location, Order, OrderDetail
)


class SquareDataAnalyzer:
    """Analyze Square data for cleaning opportunities"""
    
    def __init__(self, parsed_data: Dict):
        """
        Initialize analyzer with parsed Square data.
        
        Args:
            parsed_data: Dictionary from SquareParser.parse_all()
        """
        self.categories = parsed_data.get('categories', [])
        self.items = parsed_data.get('items', [])
        self.item_variations = parsed_data.get('item_variations', [])
        self.locations = parsed_data.get('locations', [])
        self.orders = parsed_data.get('orders', [])
        self.order_details = parsed_data.get('order_details', [])
        self.payments = parsed_data.get('payments', [])
    
    def analyze_categories(self) -> Dict:
        """Analyze categories for inconsistencies"""
        issues = {
            'emoji_inconsistency': [],
            'case_inconsistency': [],
            'duplicates': [],
            'empty_names': []
        }
        
        names = [cat.name for cat in self.categories]
        name_lower = [name.lower() for name in names]
        
        # Check for emojis
        for cat in self.categories:
            if cat.name and any(ord(c) > 127 for c in cat.name):
                issues['emoji_inconsistency'].append(cat)
        
        # Check for case inconsistencies (e.g., "Burgers" vs "burgers")
        name_counts = Counter(name_lower)
        for name, count in name_counts.items():
            if count > 1:
                variations = [cat.name for cat in self.categories if cat.name.lower() == name]
                if len(set(variations)) > 1:
                    issues['case_inconsistency'].append({
                        'normalized': name,
                        'variations': list(set(variations))
                    })
        
        # Check for empty names
        for cat in self.categories:
            if not cat.name or not cat.name.strip():
                issues['empty_names'].append(cat)
        
        return issues
    
    def analyze_items(self) -> Dict:
        """Analyze items for inconsistencies"""
        issues = {
            'typos': [],
            'name_inconsistencies': [],
            'missing_descriptions': [],
            'missing_category': [],
            'duplicate_names_different_ids': []
        }
        
        # Common typos to check
        common_typos = {
            'griled': 'grilled',
            'chiken': 'chicken',
            'expresso': 'espresso',
            'coffe': 'coffee',
            'appitizers': 'appetizers'
        }
        
        # Check for typos
        for item in self.items:
            name_lower = item.name.lower()
            for typo, correct in common_typos.items():
                if typo in name_lower:
                    issues['typos'].append({
                        'item': item,
                        'typo': typo,
                        'suggestion': item.name.replace(typo, correct).replace(typo.capitalize(), correct.capitalize())
                    })
        
        # Check for name inconsistencies (same item, different names)
        item_names_lower = defaultdict(list)
        for item in self.items:
            item_names_lower[item.name.lower().strip()].append(item)
        
        for name_lower, items in item_names_lower.items():
            if len(items) > 1:
                # Same normalized name but different IDs
                unique_ids = set(item.id for item in items)
                if len(unique_ids) > 1:
                    issues['duplicate_names_different_ids'].append({
                        'normalized_name': name_lower,
                        'items': items
                    })
        
        # Check for similar names (fuzzy matching)
        item_names = [item.name.lower().strip() for item in self.items]
        for i, item1 in enumerate(self.items):
            for item2 in self.items[i+1:]:
                name1 = item1.name.lower().strip()
                name2 = item2.name.lower().strip()
                # Check for variations like "Hash Browns" vs "Hashbrowns"
                if name1 != name2:
                    # Remove spaces and compare
                    name1_no_space = name1.replace(' ', '')
                    name2_no_space = name2.replace(' ', '')
                    if name1_no_space == name2_no_space:
                        issues['name_inconsistencies'].append({
                            'item1': item1,
                            'item2': item2,
                            'issue': 'spacing_inconsistency'
                        })
                    # Check for singular/plural or slight variations
                    elif abs(len(name1) - len(name2)) <= 2:
                        # Simple similarity check
                        common_chars = sum(1 for c in name1 if c in name2)
                        similarity = common_chars / max(len(name1), len(name2))
                        if similarity > 0.8:
                            issues['name_inconsistencies'].append({
                                'item1': item1,
                                'item2': item2,
                                'issue': 'similar_names',
                                'similarity': similarity
                            })
        
        # Check for missing descriptions
        for item in self.items:
            if not item.description:
                issues['missing_descriptions'].append(item)
        
        # Check for missing category
        for item in self.items:
            if not item.category_id:
                issues['missing_category'].append(item)
        
        return issues
    
    def analyze_item_variations(self) -> Dict:
        """Analyze item variations for inconsistencies"""
        issues = {
            'missing_prices': [],
            'zero_prices': [],
            'price_inconsistencies': [],
            'missing_currency': []
        }
        
        # Group variations by item
        variations_by_item = defaultdict(list)
        for var in self.item_variations:
            variations_by_item[var.item_id].append(var)
        
        # Check for missing or zero prices
        for var in self.item_variations:
            if var.price is None:
                issues['missing_prices'].append(var)
            elif var.price == 0:
                issues['zero_prices'].append(var)
            
            if not var.price_currency:
                issues['missing_currency'].append(var)
        
        # Check for price inconsistencies (same variation name, different prices)
        var_names_by_item = defaultdict(lambda: defaultdict(list))
        for var in self.item_variations:
            var_names_by_item[var.item_id][var.name.lower()].append(var)
        
        for item_id, name_vars in var_names_by_item.items():
            for var_name, vars_list in name_vars.items():
                if len(vars_list) > 1:
                    prices = [v.price for v in vars_list]
                    if len(set(prices)) > 1:
                        issues['price_inconsistencies'].append({
                            'item_id': item_id,
                            'variation_name': var_name,
                            'variations': vars_list
                        })
        
        return issues
    
    def analyze_all(self) -> Dict:
        """Run all analyses"""
        return {
            'categories': self.analyze_categories(),
            'items': self.analyze_items(),
            'item_variations': self.analyze_item_variations()
        }


class SquareDataCleaner:
    """Clean and normalize Square data"""
    
    def __init__(self, parsed_data: Dict):
        """
        Initialize cleaner with parsed Square data.
        
        Args:
            parsed_data: Dictionary from SquareParser.parse_all()
        """
        self.parsed_data = parsed_data
        self.analyzer = SquareDataAnalyzer(parsed_data)
    
    def clean_category_names(self) -> List[Category]:
        """Clean category names - remove emojis, standardize case"""
        cleaned = []
        for cat in self.parsed_data['categories']:
            # Remove emojis
            name = ''.join(c for c in cat.name if ord(c) < 127 or c.isspace())
            name = name.strip()
            
            # Standardize case (Title Case)
            if name:
                name = name.title()
            
            cleaned.append(Category(
                id=cat.id,
                name=name
            ))
        return cleaned
    
    def clean_item_names(self) -> List[Item]:
        """Clean item names - fix typos, standardize"""
        # Common typos mapping
        typo_fixes = {
            'griled': 'grilled',
            'chiken': 'chicken',
            'expresso': 'espresso',
            'coffe': 'coffee',
            'coffeeee': 'coffee',  # Multiple e's
            'appitizers': 'appetizers',
            'sandwhich': 'sandwich'
        }
        
        cleaned = []
        for item in self.parsed_data['items']:
            name = item.name
            
            # Fix typos (case-insensitive)
            name_lower = name.lower()
            for typo, correct in typo_fixes.items():
                if typo in name_lower:
                    # Replace with case preservation
                    import re
                    pattern = re.compile(re.escape(typo), re.IGNORECASE)
                    name = pattern.sub(correct, name)
            
            # Standardize spacing (remove extra spaces)
            name = ' '.join(name.split())
            
            # Title case for consistency (but preserve acronyms)
            words = name.split()
            title_words = []
            for word in words:
                if word.isupper() and len(word) > 1:
                    title_words.append(word)  # Keep acronyms
                else:
                    title_words.append(word.capitalize())
            name = ' '.join(title_words)
            
            cleaned.append(Item(
                id=item.id,
                name=name,
                description=item.description,
                category_id=item.category_id
            ))
        return cleaned
    
    def normalize_item_names(self) -> Dict[str, str]:
        """
        Create a mapping of item IDs to normalized names.
        Groups similar items together (e.g., "Hash Browns" and "Hashbrowns").
        
        Returns:
            Dict mapping item_id -> normalized_name
        """
        normalization_map = {}
        items_by_normalized = defaultdict(list)
        
        # First pass: exact matches
        for item in self.parsed_data['items']:
            # Normalize: lowercase, remove extra spaces
            normalized = item.name.lower().strip()
            normalized = ' '.join(normalized.split())
            items_by_normalized[normalized].append(item)
        
        # Second pass: handle spacing variations (e.g., "Hash Browns" vs "Hashbrowns")
        name_groups = {}
        for normalized, items in items_by_normalized.items():
            # Remove spaces for grouping
            key = normalized.replace(' ', '')
            if key not in name_groups:
                name_groups[key] = []
            name_groups[key].extend(items)
        
        # Create mapping using the most common name in each group
        for key, items in name_groups.items():
            # Use the longest name as standard (usually most descriptive)
            standard_item = max(items, key=lambda x: len(x.name))
            standard_name = standard_item.name
            
            for item in items:
                normalization_map[item.id] = standard_name
        
        return normalization_map
    
    def get_cleaned_data(self) -> Dict:
        """
        Return cleaned and normalized data.
        
        Returns:
            Dictionary with cleaned categories, items, etc.
        """
        return {
            'categories': self.clean_category_names(),
            'items': self.clean_item_names(),
            'item_variations': self.parsed_data['item_variations'],  # No cleaning needed
            'locations': self.parsed_data['locations'],  # No cleaning needed
            'orders': self.parsed_data['orders'],  # No cleaning needed
            'order_details': self.parsed_data['order_details'],  # No cleaning needed
            'payments': self.parsed_data['payments']  # No cleaning needed
        }
    
    def generate_cleaning_report(self) -> str:
        """Generate a report of all issues found"""
        analysis = self.analyzer.analyze_all()
        report = []
        report.append("=" * 80)
        report.append("SQUARE DATA CLEANING REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Categories
        report.append("CATEGORIES:")
        report.append("-" * 80)
        cat_issues = analysis['categories']
        report.append(f"  Emoji inconsistencies: {len(cat_issues['emoji_inconsistency'])}")
        for cat in cat_issues['emoji_inconsistency'][:5]:
            report.append(f"    - {cat.name} (ID: {cat.id})")
        
        report.append(f"  Case inconsistencies: {len(cat_issues['case_inconsistency'])}")
        for issue in cat_issues['case_inconsistency'][:5]:
            report.append(f"    - Variations: {issue['variations']}")
        
        report.append("")
        
        # Items
        report.append("ITEMS:")
        report.append("-" * 80)
        item_issues = analysis['items']
        report.append(f"  Typos found: {len(item_issues['typos'])}")
        for issue in item_issues['typos'][:10]:
            report.append(f"    - '{issue['item'].name}' -> '{issue['suggestion']}' (ID: {issue['item'].id})")
        
        report.append(f"  Name inconsistencies: {len(item_issues['name_inconsistencies'])}")
        for issue in item_issues['name_inconsistencies'][:10]:
            report.append(f"    - '{issue['item1'].name}' (ID: {issue['item1'].id}) vs '{issue['item2'].name}' (ID: {issue['item2'].id})")
        
        report.append(f"  Missing descriptions: {len(item_issues['missing_descriptions'])}")
        report.append(f"  Missing categories: {len(item_issues['missing_category'])}")
        report.append("")
        
        # Item Variations
        report.append("ITEM VARIATIONS:")
        report.append("-" * 80)
        var_issues = analysis['item_variations']
        report.append(f"  Missing prices: {len(var_issues['missing_prices'])}")
        report.append(f"  Zero prices: {len(var_issues['zero_prices'])}")
        report.append(f"  Price inconsistencies: {len(var_issues['price_inconsistencies'])}")
        report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)


if __name__ == '__main__':
    import sys
    import io
    # Set UTF-8 encoding for stdout to handle emojis
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    from square_parser import SquareParser
    
    # Parse Square data
    parser = SquareParser(
        catalog_path='data/sources/square/catalog.json',
        orders_path='data/sources/square/orders.json',
        payments_path='data/sources/square/payments.json',
        locations_path='data/sources/square/locations.json'
    )
    
    parsed_data = parser.parse_all()
    
    # Analyze and clean
    cleaner = SquareDataCleaner(parsed_data)
    
    # Generate report
    report = cleaner.generate_cleaning_report()
    print(report)
    
    # Show normalization mapping
    print("\n" + "=" * 80)
    print("ITEM NAME NORMALIZATION MAPPING (showing changes only)")
    print("=" * 80)
    norm_map = cleaner.normalize_item_names()
    changes = []
    for item_id, normalized_name in norm_map.items():
        original = next(item.name for item in parsed_data['items'] if item.id == item_id)
        if original != normalized_name:
            changes.append((item_id, original, normalized_name))
    
    if changes:
        for item_id, original, normalized in changes[:15]:
            print(f"  {item_id}: '{original}' -> '{normalized}'")
    else:
        print("  No normalization changes needed")
    
    # Show cleaned data sample
    print("\n" + "=" * 80)
    print("CLEANED DATA SAMPLE")
    print("=" * 80)
    cleaned_data = cleaner.get_cleaned_data()
    
    print("\nCleaned Categories (first 5):")
    for cat in cleaned_data['categories'][:5]:
        print(f"  - {cat.name} (ID: {cat.id})")
    
    print("\nCleaned Items (first 10):")
    for item in cleaned_data['items'][:10]:
        print(f"  - {item.name} (ID: {item.id})")

