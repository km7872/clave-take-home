"""
API router that maps structured queries to API endpoints.
Analyzes structured_query and routes to appropriate API services.
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from src.api.services import (
    metrics_service, products_service, locations_service,
    orders_service, payments_service, time_service
)


class APIRouter:
    """
    Routes structured queries to appropriate API endpoints.
    """
    
    def __init__(self):
        """Initialize the API router."""
        pass
    
    def route(self, structured_query: Dict) -> Optional[Dict]:
        """
        Route structured query to an API endpoint if available.
        
        Args:
            structured_query: Structured query dictionary from LLM
            
        Returns:
            API routing info dict with 'api_function' and 'params', or None if no match
        """
        intent = structured_query.get("intent", "").lower()
        tables = structured_query.get("tables", [])
        filters = structured_query.get("filters") or {}
        group_by = structured_query.get("group_by", [])
        limit = structured_query.get("limit")
        
        # Extract dates from filters
        start_date, end_date = self._extract_dates(filters)
        
        # Extract location from filters
        location_id, location_names = self._extract_locations(filters)
        
        # Route based on intent and tables
        routing_result = None
        
        # Revenue/Sales queries
        if "revenue" in intent or "sales" in intent:
            # If specific locations are mentioned, use comparison API instead
            if location_names and len(location_names) > 0:
                # Route to location comparison which handles specific locations
                metric = "revenue" if "revenue" in intent or "sales" in intent else "orders"
                routing_result = {
                    "api_function": locations_service.compare_locations,
                    "params": {
                        "locations": location_names,
                        "start_date": start_date,
                        "end_date": end_date,
                        "metric": metric
                    }
                }
            elif any("location" in col.lower() for col in group_by):
                # Revenue by location (all locations)
                routing_result = {
                    "api_function": metrics_service.get_revenue_by_location,
                    "params": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif "trend" in intent or "time" in intent or any("created_at" in col for col in group_by):
                # Revenue trend
                granularity = "hour" if "hour" in intent else "day"
                routing_result = {
                    "api_function": metrics_service.get_revenue_trend,
                    "params": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "granularity": granularity,
                        "location_id": location_id
                    }
                }
            elif "orders" in tables or "orders" in str(tables):
                # Simple revenue query
                routing_result = {
                    "api_function": metrics_service.get_revenue,
                    "params": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "location_id": location_id
                    }
                }
        
        # Top products queries
        elif "top" in intent and ("product" in intent or "selling" in intent or "item" in intent):
            metric = "revenue" if "revenue" in intent or "sales" in intent else "quantity"
            routing_result = {
                "api_function": products_service.get_top_selling_products,
                "params": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit or 10,
                    "metric": metric,
                    "location_id": location_id
                }
            }
        
        # Location comparison queries
        elif "comparison" in intent and location_names and len(location_names) > 1:
            metric = "revenue" if "revenue" in intent or "sales" in intent else "orders"
            routing_result = {
                "api_function": locations_service.compare_locations,
                "params": {
                    "locations": location_names,
                    "start_date": start_date,
                    "end_date": end_date,
                    "metric": metric
                }
            }
        elif "location" in intent and ("performance" in intent or "ranking" in intent):
            routing_result = {
                "api_function": locations_service.get_location_performance,
                "params": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        
        # Fulfillment queries
        elif "fulfillment" in intent or "delivery" in intent or "dine" in intent:
            routing_result = {
                "api_function": orders_service.get_fulfillment_breakdown,
                "params": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "location_id": location_id
                }
            }
        
        # Average order value
        elif "average" in intent and "order" in intent:
            routing_result = {
                "api_function": orders_service.get_average_order_value,
                "params": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "location_id": location_id
                }
            }
        
        # Payment methods
        elif "payment" in intent and "method" in intent:
            routing_result = {
                "api_function": payments_service.get_payment_method_breakdown,
                "params": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "location_id": location_id
                }
            }
        
        # Tips analysis
        elif "tip" in intent:
            routing_result = {
                "api_function": payments_service.get_tips_analysis,
                "params": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "location_id": location_id
                }
            }
        
        # Peak hours
        elif "peak" in intent and "hour" in intent:
            routing_result = {
                "api_function": time_service.get_peak_hours,
                "params": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "location_id": location_id
                }
            }
        
        # Day of week
        elif "day" in intent and "week" in intent:
            routing_result = {
                "api_function": time_service.get_day_of_week_analysis,
                "params": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "location_id": location_id
                }
            }
        
        return routing_result
    
    def _extract_dates(self, filters: Dict) -> Tuple[datetime, datetime]:
        """
        Extract start and end dates from filters.
        
        Args:
            filters: Filters dictionary from structured_query
            
        Returns:
            Tuple of (start_date, end_date) in datetime objects
        """
        start_date = None
        end_date = None
        
        # Look for created_at filters
        for column, filter_def in filters.items():
            if "created_at" in column.lower() or "date" in column.lower():
                operator = filter_def.get("operator", "")
                value = filter_def.get("value")
                
                if operator == "gte" and value:
                    start_date = self._parse_date(value)
                elif operator == "lte" and value:
                    end_date = self._parse_date(value)
                elif operator == "eq" and value:
                    start_date = self._parse_date(value)
                    end_date = self._parse_date(value)
        
        # Default dates if not provided
        if not start_date:
            start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        if not end_date:
            end_date = datetime.now(timezone.utc)
        
        return start_date, end_date
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """
        Parse date value to datetime object.
        
        Args:
            date_value: Date string or value
            
        Returns:
            datetime object or None
        """
        if isinstance(date_value, datetime):
            return date_value
        
        if not isinstance(date_value, str):
            return None
        
        try:
            # Try ISO format first
            if "T" in date_value:
                return datetime.fromisoformat(date_value.replace("Z", "+00:00"))
            else:
                # Try date-only format
                return datetime.strptime(date_value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            return None
    
    def _extract_locations(self, filters: Dict) -> Tuple[Optional[str], List[str]]:
        """
        Extract location ID and names from filters.
        
        Args:
            filters: Filters dictionary from structured_query
            
        Returns:
            Tuple of (location_id, location_names_list)
        """
        location_id = None
        location_names = []
        
        for column, filter_def in filters.items():
            if "location" in column.lower():
                operator = filter_def.get("operator", "")
                value = filter_def.get("value")
                
                if operator == "eq" and value:
                    # Single location - could be name or ID
                    if isinstance(value, str):
                        location_names.append(value)
                elif operator == "in" and isinstance(value, list):
                    # Multiple locations
                    location_names.extend(value)
        
        # If we have location names, try to get the ID (for single location queries)
        if len(location_names) == 1:
            try:
                location_id = locations_service.get_location_id(location_names[0])
                if not location_id:
                    location_id = None
            except (Exception, AttributeError):
                location_id = None
        
        return location_id, location_names

