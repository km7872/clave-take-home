"""
Main query interface for natural language queries.
Combines LLM parsing, API routing, and query building.
"""
from typing import Dict, Tuple, Optional
from src.query.llm_parser import LLMQueryParser
from src.query.query_builder import QueryBuilder
from src.query.api_router import APIRouter
from src.query.api_executor import APIExecutor


class NaturalLanguageQuery:
    """
    Main interface for natural language query processing.
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0):
        """
        Initialize the natural language query interface.
        
        Args:
            model: OpenAI model to use
            temperature: Model temperature
        """
        self.llm_parser = LLMQueryParser(model=model, temperature=temperature)
        self.query_builder = QueryBuilder()
        self.api_router = APIRouter()
        self.api_executor = APIExecutor(model=model, temperature=temperature)
    
    def execute(self, user_query: str) -> Tuple[Dict, Optional[str]]:
        """
        Execute a natural language query.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Tuple of (result_dict, error_message)
            result_dict: {"success": bool, "data": list, "structured_query": dict, ...}
            error_message: None if successful, error string if failed
        """
        try:
            # Step 1: Parse natural language to structured JSON
            structured_query = self.llm_parser.parse_query(user_query)
            
            # Step 2: Try to route to API endpoint
            routing_info = self.api_router.route(structured_query)
            
            if routing_info:
                # Step 2a: Execute API call
                result = self.api_executor.execute(routing_info, structured_query, user_query)
                # pass result and intent to another llm parser to figur eout what is nedd from the data
                return result, None
            else:
                # Step 2b: Fall back to QueryBuilder
                result = self.query_builder.build_and_execute(structured_query)
                
                # Step 3: Return results with structured query metadata
                return {
                    "success": result.get("success", False),
                    "data": result.get("data", []),
                    "count": result.get("count", 0),
                    "structured_query": structured_query,
                    "user_query": user_query,
                    "metadata": result.get("metadata", {}),
                    "error": result.get("error")  # Include error if query failed
                }, None
            
        except ValueError as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "user_query": user_query
            }, str(e)
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "user_query": user_query
            }, f"Error processing query: {str(e)}"

