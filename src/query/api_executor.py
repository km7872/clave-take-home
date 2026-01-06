"""
API executor that calls API services and transforms responses to expected format.
"""
from typing import Dict, Any, Optional, Callable
from src.query.api_router import APIRouter
from src.query.data_formatter import DataFormatter


class APIExecutor:
    """
    Executes API calls and transforms responses to match query interface format.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Initialize the API executor.
        
        Args:
            model: OpenAI model to use for data formatting
            temperature: Model temperature
        """
        self.data_formatter = DataFormatter(model=model, temperature=temperature)
    
    def execute(self, routing_info: Dict, structured_query: Dict, user_query: str) -> Dict:
        """
        Execute API call and transform response.
        
        Args:
            routing_info: Routing info from APIRouter.route()
            structured_query: Original structured query
            user_query: Original user query
            
        Returns:
            Transformed response in query interface format
        """
        api_function = routing_info["api_function"]
        params = routing_info["params"]
        
        try:
            # Call the API function
            api_response = api_function(**params)
            
            # Handle case where API returns a list directly (not wrapped in dict)
            if isinstance(api_response, list):
                api_response = {"data": api_response}
            
            # Get raw data from API response
            raw_data = api_response.get("data", [])
            if not isinstance(raw_data, list):
                raw_data = [raw_data] if raw_data else []
            
            # Use LLM to filter/format data based on user query
            formatted_data = self.data_formatter.format_response(
                raw_data, user_query, structured_query
            )
            
            # Update API response with formatted data
            api_response["data"] = formatted_data
            
            # Transform response to expected format
            return self._transform_response(api_response, structured_query, user_query)
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "structured_query": structured_query,
                "user_query": user_query,
                "error": f"API execution failed: {str(e)}"
            }
    
    def _transform_response(self, api_response: Dict, structured_query: Dict, user_query: str) -> Dict:
        """
        Transform API response to query interface format.
        
        Args:
            api_response: Response from API service
            structured_query: Original structured query
            user_query: Original user query
            
        Returns:
            Transformed response dict
        """
        # Extract data from API response
        raw_data = api_response.get("data")
        
        # Handle different API response formats
        if raw_data is None:
            data = []
        elif isinstance(raw_data, dict):
            # Some APIs return data as a dict (like tips_analysis)
            data = [raw_data]
        elif isinstance(raw_data, list):
            data = raw_data if raw_data else []
        else:
            data = [raw_data]
        
        # Check if data is empty
        if not data:
            return {
                "success": True,
                "data": [],
                "count": 0,
                "structured_query": structured_query,
                "user_query": user_query,
                "message": "No data found"
            }
        
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "structured_query": structured_query,
            "user_query": user_query,
            "metadata": api_response.get("metadata", {}),
            "summary": api_response.get("summary", {})
        }

