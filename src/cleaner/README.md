# Name Cleaning Script

This module provides a script to clean and standardize item and item variation names using fuzzy matching and GPT.

## Overview

The script:
1. Fetches items/variations from the database where `display_name` IS NULL
2. Groups similar names using fuzzy matching (within categories for items, within items for variations)
3. Uses GPT to suggest cleaned, standardized `display_name` values
4. Shows a preview of changes
5. Requires user confirmation before updating the database
6. Only updates the `display_name` field (never modifies the original `name` field)

## Usage

```bash
# Clean both items and item variations (default)
python src/cleaner/clean_names.py

# Clean only items
python src/cleaner/clean_names.py --table items

# Clean only item variations
python src/cleaner/clean_names.py --table item_variations
```

## Requirements

- `OPENAI_API_KEY` environment variable must be set
- `SUPABASE_SERVICE_ROLE_KEY` environment variable must be set
- Python packages: `openai`, `rapidfuzz`, `supabase` (see requirements.txt)

## How It Works

### Items
- Groups items by `category_id`
- Within each category, uses fuzzy matching to find similar names
- Sends grouped names to GPT for cleaning/standardization
- Updates all items in the group with the cleaned `display_name`

### Item Variations
- Groups variations by `item_id`
- For each item, sends all variation names to GPT for standardization
- Updates all variations with cleaned `display_name` values

## Safety Features

- **Preview before update**: Shows exactly what will change
- **User confirmation**: Requires typing "yes" to proceed
- **Non-destructive**: Only updates `display_name`, never modifies `name`
- **Idempotent**: Safe to run multiple times (only processes NULL `display_name` fields)

