"""
Main query interface for natural language queries.
Combines LLM parsing and query building.
"""
from typing import Dict, Tuple, Optional
from src.query.llm_parser import LLMQueryParser
from src.query.query_builder import QueryBuilder


class NaturalLanguageQuery:
    """
    Main interface for natural language query processing.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Initialize the natural language query interface.
        
        Args:
            model: OpenAI model to use
            temperature: Model temperature
        """
        self.llm_parser = LLMQueryParser(model=model, temperature=temperature)
        self.query_builder = QueryBuilder()
    
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
            
            # Step 2: Build and execute Supabase query
            result = self.query_builder.build_and_execute(structured_query)
            
            # Step 3: Return results with structured query metadata
            return {
                "success": result.get("success", False),
                "data": result.get("data", []),
                "count": result.get("count", 0),
                "structured_query": structured_query,
                "user_query": user_query,
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

