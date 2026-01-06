"""
Query builder that converts structured JSON queries to Supabase queries.
"""
from typing import Dict, List, Any, Optional
from src.db.dbConnect import db
from src.query.schema import validate_table, validate_column, DATABASE_SCHEMA


class QueryBuilder:
    """
    Builds Supabase queries from structured JSON query objects.
    """
    
    def __init__(self):
        self.schema = DATABASE_SCHEMA
    
    def build_and_execute(self, structured_query: Dict) -> Dict:
        """
        Build and execute a Supabase query from structured JSON.
        
        Args:
            structured_query: Structured query dictionary from LLM
            
        Returns:
            Query results with data and metadata
        """
        # Validate query structure
        self._validate_query(structured_query)
        
        # Get primary table from structured query
        primary_table = structured_query["tables"][0]
        joins = structured_query.get("joins", [])
        
        # For Supabase: foreign table syntax works from the table WITH the foreign key
        # If SQL is "from item_variations join order_details on item_variations.id = order_details.itemvar_id"
        # Then order_details has the FK (itemvar_id), so we query from order_details and embed item_variations
        query_table = primary_table
        if joins:
            for join in joins:
                join_table = join["table"]
                join_on = join.get("on", "")
                # Check join direction: if join_on contains "order_details.itemvar_id"
                # then order_details has the FK, so query from order_details
                if "order_details.itemvar_id" in join_on:
                    # Primary is item_variations, but order_details has the FK, so query from order_details
                    query_table = "order_details"
                    break
                elif "itemvar_id" in join_on and primary_table == "item_variations":
                    # If we see itemvar_id in the join and primary is item_variations, query from order_details
                    query_table = "order_details"
                    break
        
        query = db.table(query_table)
        
        # Build select statement (handle joins)
        if len(structured_query["tables"]) > 1:
            # Multi-table query - use joins
            select_fields = self._build_select_with_joins(structured_query, query_table, primary_table)
        else:
            # Single table query
            select_fields = self._build_select(structured_query)
        
        query = query.select(select_fields)
        
        # Apply filters (handle null/None filters)
        filters = structured_query.get("filters")
        if filters is None:
            filters = {}
        query = self._apply_filters(query, filters, primary_table)
        
        # Apply order by
        # Note: Supabase doesn't support ordering by aliases, so we skip ordering if it's an alias
        # We'll handle sorting in post-processing if needed
        if "order_by" in structured_query and structured_query["order_by"]:
            order_col = structured_query["order_by"]["column"]
            direction = structured_query["order_by"].get("direction", "asc")
            
            # Check if this is an alias (not a real column)
            # Aliases like "gross", "total_sales" won't work with Supabase's order()
            # We'll skip ordering here and do it in post-processing
            primary_table = structured_query["tables"][0]
            is_alias = order_col not in self.schema.get(primary_table, {}).get("columns", [])
            
            if not is_alias:
                # It's a real column, we can order by it
                if "." in order_col:
                    order_col = order_col.split(".")[-1]
                query = query.order(order_col, desc=(direction == "desc"))
            # If it's an alias, we'll handle sorting in post-processing
        
        # Apply limit
        if "limit" in structured_query and structured_query["limit"]:
            query = query.limit(structured_query["limit"])
        
        # Execute query
        try:
            response = query.execute()
            data = response.data if response.data else []
            
            # Post-process aggregations and sorting if needed
            # Supabase doesn't support aggregations or ordering by aliases directly
            # We need to fetch all data, then aggregate and group in Python
            if "aggregations" in structured_query and structured_query.get("aggregations") and structured_query.get("group_by"):
                data = self._apply_aggregations(data, structured_query)
            
            # Handle sorting by alias if needed (after aggregations)
            if "order_by" in structured_query and structured_query["order_by"]:
                order_col = structured_query["order_by"]["column"]
                direction = structured_query["order_by"].get("direction", "asc")
                primary_table = structured_query["tables"][0]
                is_alias = order_col not in self.schema.get(primary_table, {}).get("columns", [])
                
                if is_alias and data:
                    # Sort by alias in post-processing
                    reverse = (direction == "desc")
                    try:
                        data = sorted(data, key=lambda x: x.get(order_col, 0), reverse=reverse)
                    except (KeyError, TypeError):
                        # If alias doesn't exist, skip sorting
                        pass
            
            # Apply limit after sorting (if limit was specified)
            if "limit" in structured_query and structured_query["limit"] and len(data) > structured_query["limit"]:
                data = data[:structured_query["limit"]]
            
            # Determine visualization metadata if not provided
            metadata = self._determine_visualization(structured_query, data)
            
            return {
                "success": True,
                "data": data,
                "count": len(data),
                "metadata": metadata
            }
        except Exception as e:
            import traceback
            error_details = str(e)
            # Include more context in error message
            return {
                "success": False,
                "error": f"Query execution failed: {error_details}",
                "data": [],
                "count": 0
            }
    
    def _validate_query(self, query: Dict) -> None:
        """Validate the structured query."""
        required_fields = ["tables", "select"]
        for field in required_fields:
            if field not in query:
                raise ValueError(f"Missing required field: {field}")
        
        if not query["tables"]:
            raise ValueError("At least one table must be specified")
        
        # Validate tables exist
        for table in query["tables"]:
            if not validate_table(table):
                raise ValueError(f"Unknown table: {table}")
    
    def _build_select(self, structured_query: Dict) -> str:
        """
        Build select statement for Supabase.
        For simple queries (single table), return column list.
        """
        select_fields = structured_query.get("select", [])
        if not select_fields:
            return "*"
        
        # For now, return all fields - Supabase aggregation handling is complex
        # We'll handle aggregations in post-processing
        return "*"
    
    def _build_select_with_joins(self, structured_query: Dict, query_table: str, primary_table: str) -> str:
        """
        Build select statement with joins using Supabase foreign table syntax.
        Format: "*, foreign_table(*)" for foreign key relationships
        
        Note: Supabase uses foreign table embedding which requires foreign keys to be properly set up.
        The syntax is: "*, foreign_table_name(*)" where foreign_table_name is the referenced table.
        
        Args:
            query_table: The table we're actually querying from (may differ from primary_table)
            primary_table: The primary table from the structured query (for output structure)
        """
        joins = structured_query.get("joins", [])
        
        # Start with all fields from the table we're querying
        base_select = "*"
        
        # Add joined tables using Supabase foreign table syntax
        # If querying from order_details, we can embed item_variations using the FK
        for join in joins:
            join_table = join["table"]
            # If we're querying from the joined table, embed the primary table
            if query_table == join_table and primary_table != join_table:
                # Query from join_table, embed primary_table
                base_select = f"*, {primary_table}(*)"
            elif query_table != join_table:
                # Query from query_table, embed join_table
                base_select += f", {join_table}(*)"
        
        return base_select
    
    def _apply_aggregations(self, data: List[Dict], structured_query: Dict) -> List[Dict]:
        """
        Apply aggregations in Python (since Supabase doesn't support SQL aggregations directly).
        Handles SUM, COUNT, AVG, MAX, MIN with GROUP BY.
        """
        aggregations = structured_query.get("aggregations", [])
        group_by = structured_query.get("group_by", [])
        select_fields = structured_query.get("select", [])
        
        if not aggregations or not group_by or not data:
            return data
        
        # Parse select fields to find aggregation columns and group by columns
        # Example: "SUM(order_details.gross_amount) AS gross"
        agg_columns = {}
        group_by_cols = []
        
        for field in select_fields:
            if "SUM(" in field.upper() or "COUNT(" in field.upper() or "AVG(" in field.upper():
                # Extract aggregation: "SUM(order_details.gross_amount) AS gross"
                parts = field.upper().split(" AS ")
                if len(parts) == 2:
                    alias = parts[1].strip()
                    agg_part = parts[0].strip()
                    if "SUM(" in agg_part:
                        # Extract column: "SUM(order_details.gross_amount)" -> "order_details.gross_amount"
                        col = agg_part.replace("SUM(", "").replace(")", "").strip()
                        agg_columns[alias] = {"type": "SUM", "column": col}
                    elif "COUNT(" in agg_part:
                        col = agg_part.replace("COUNT(", "").replace(")", "").strip()
                        agg_columns[alias] = {"type": "COUNT", "column": col}
                    elif "AVG(" in agg_part:
                        col = agg_part.replace("AVG(", "").replace(")", "").strip()
                        agg_columns[alias] = {"type": "AVG", "column": col}
        
        # Extract group by columns (remove table prefix if present)
        # Also track the full column names for output
        group_by_cols = []
        group_by_output_names = []  # For output field names
        for col in group_by:
            if "." in col:
                # "item_variations.id" -> use "id" for grouping, but keep full name for output
                col_name = col.split(".")[-1]
                group_by_cols.append(col_name)
                group_by_output_names.append(col)  # Keep full name for output
            else:
                group_by_cols.append(col)
                group_by_output_names.append(col)
        
        # Group and aggregate data
        grouped = {}
        for record in data:
            # Create group key from group_by columns
            # Handle nested data from joins (e.g., record['item_variations']['id'])
            group_key_parts = []
            for gb_col in group_by_cols:
                # Try direct access first
                if gb_col in record:
                    group_key_parts.append(str(record[gb_col]))
                else:
                    # Try nested access (for joined tables)
                    found = False
                    for key, value in record.items():
                        if isinstance(value, dict) and gb_col in value:
                            group_key_parts.append(str(value[gb_col]))
                            found = True
                            break
                    if not found:
                        group_key_parts.append("")
            
            group_key = tuple(group_key_parts)
            
            if group_key not in grouped:
                grouped[group_key] = {
                    "records": [],
                    "group_values": {}
                }
                # Store group by values
                for i, gb_col in enumerate(group_by_cols):
                    if gb_col in record:
                        grouped[group_key]["group_values"][gb_col] = record[gb_col]
                    else:
                        # Try nested access
                        for key, value in record.items():
                            if isinstance(value, dict) and gb_col in value:
                                grouped[group_key]["group_values"][gb_col] = value[gb_col]
                                break
            
            grouped[group_key]["records"].append(record)
        
        # Apply aggregations
        result = []
        for group_key, group_data in grouped.items():
            result_record = {}
            
            # Add group by columns to result (use simplified names)
            for i, gb_col in enumerate(group_by_cols):
                # Use the column name without table prefix for output
                output_name = gb_col  # e.g., "id" or "name"
                if gb_col in group_data["group_values"]:
                    result_record[output_name] = group_data["group_values"][gb_col]
                else:
                    # Try to find it in nested structure
                    for key, value in group_data["records"][0].items() if group_data["records"] else {}:
                        if isinstance(value, dict) and gb_col in value:
                            result_record[output_name] = value[gb_col]
                            break
            
            # Add aggregated columns
            for alias, agg_info in agg_columns.items():
                agg_type = agg_info["type"]
                col = agg_info["column"]
                
                # Extract column name (remove table prefix)
                if "." in col:
                    col_name = col.split(".")[-1]
                else:
                    col_name = col
                
                # Get values from records
                values = []
                for rec in group_data["records"]:
                    # Try direct access first
                    if col_name in rec:
                        val = rec[col_name]
                        if val is not None:
                            try:
                                values.append(float(val))
                            except (ValueError, TypeError):
                                pass
                    else:
                        # Try nested access (for joined tables)
                        for key, value in rec.items():
                            if isinstance(value, dict) and col_name in value:
                                val = value[col_name]
                                if val is not None:
                                    try:
                                        values.append(float(val))
                                    except (ValueError, TypeError):
                                        pass
                                break
                
                # Apply aggregation
                if agg_type == "SUM":
                    result_record[alias] = sum(values) if values else 0
                elif agg_type == "COUNT":
                    result_record[alias] = len(values)
                elif agg_type == "AVG":
                    result_record[alias] = sum(values) / len(values) if values else 0
            
            result.append(result_record)
        
        return result
    
    def _apply_filters(self, query, filters: Dict, table_name: str):
        """Apply filters to the query."""
        for column, filter_def in filters.items():
            operator = filter_def.get("operator", "eq")
            value = filter_def.get("value")
            
            # Handle table.column format
            if "." in column:
                # This is a joined column - Supabase filters work differently
                # For now, we'll filter on the column directly
                column = column.split(".")[-1]
            
            if operator == "eq":
                query = query.eq(column, value)
            elif operator == "in":
                query = query.in_(column, value if isinstance(value, list) else [value])
            elif operator == "gte":
                query = query.gte(column, value)
            elif operator == "lte":
                query = query.lte(column, value)
            elif operator == "gt":
                query = query.gt(column, value)
            elif operator == "lt":
                query = query.lt(column, value)
            elif operator == "like":
                query = query.like(column, f"%{value}%")
            # Add more operators as needed
        
        return query
    
    def _determine_visualization(self, structured_query: Dict, data: List[Dict]) -> Dict[str, Any]:
        """
        Determine visualization type based on query structure and data.
        
        Args:
            structured_query: Structured query dictionary
            data: Query result data
            
        Returns:
            Metadata dictionary with visualization info
        """
        # Check if visualization is already specified in structured_query
        if "visualization" in structured_query and structured_query["visualization"]:
            viz = structured_query["visualization"]
            return {
                "suggested_visualization": viz.get("type", "table"),
                "x_axis": viz.get("x_axis"),
                "y_axis": viz.get("y_axis")
            }
        
        # Determine visualization based on query structure
        intent = structured_query.get("intent", "").lower()
        group_by = structured_query.get("group_by", [])
        aggregations = structured_query.get("aggregations", [])
        has_time_filter = False
        
        # Check for time-based queries
        filters = structured_query.get("filters") or {}
        for col in filters.keys():
            if "created_at" in col.lower() or "date" in col.lower():
                has_time_filter = True
                break
        
        # Check group_by for time columns
        for col in group_by:
            if "created_at" in col.lower() or "date" in col.lower() or "hour" in col.lower():
                has_time_filter = True
                break
        
        # Visualization logic
        if has_time_filter or "trend" in intent or "time" in intent:
            viz_type = "line_chart"
            x_axis = "period" if group_by else None
        elif "comparison" in intent or "vs" in intent or len(group_by) > 0:
            # If comparing categories/locations
            if any("location" in col.lower() for col in group_by):
                viz_type = "bar_chart"
                x_axis = "location_name" if any("name" in col.lower() for col in group_by) else None
            elif len(data) <= 10 and aggregations:
                viz_type = "bar_chart"
                x_axis = group_by[0].split(".")[-1] if group_by else None
            else:
                viz_type = "table"
                x_axis = None
        elif "top" in intent and structured_query.get("limit"):
            viz_type = "bar_chart"
            x_axis = group_by[0].split(".")[-1] if group_by else None
        elif not aggregations and len(data) == 1:
            # Single value/metric
            viz_type = "metric_card"
            x_axis = None
        elif not aggregations and len(data) <= 5:
            # Small dataset - could be pie chart or table
            if any("type" in col.lower() or "method" in col.lower() or "category" in col.lower() 
                   for col in (structured_query.get("select", []) + group_by)):
                viz_type = "pie_chart"
                x_axis = None
            else:
                viz_type = "table"
                x_axis = None
        else:
            # Default to table for complex queries
            viz_type = "table"
            x_axis = None
        
        # Determine y_axis from select fields
        y_axis = None
        select_fields = structured_query.get("select", [])
        for field in select_fields:
            if "SUM(" in field.upper() or "COUNT(" in field.upper() or "AVG(" in field.upper():
                # Extract alias or column name
                if " AS " in field.upper():
                    y_axis = field.upper().split(" AS ")[-1].strip()
                else:
                    y_axis = field.split("(")[1].split(")")[0].split(".")[-1]
                break
        
        return {
            "suggested_visualization": viz_type,
            "x_axis": x_axis,
            "y_axis": y_axis
        }

