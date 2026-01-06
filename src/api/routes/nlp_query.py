"""
API routes for natural language query processing.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from src.query.query_interface import NaturalLanguageQuery

router = APIRouter()

# Initialize query interface (can be reused across requests)
query_interface = NaturalLanguageQuery()


class QueryRequest(BaseModel):
    """Request model for NLP query."""
    query: str
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.0


class QueryResponse(BaseModel):
    """Response model for NLP query."""
    success: bool
    data: list
    count: int
    structured_query: dict
    user_query: str
    metadata: Optional[dict] = None
    summary: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None


@router.post("/nlp-query", response_model=QueryResponse)
async def process_nlp_query(request: QueryRequest):
    """
    Process a natural language query and return results with visualization metadata.
    
    Args:
        request: QueryRequest with the user's natural language query
        
    Returns:
        QueryResponse with data, metadata, and visualization suggestions
    """
    try:
        # Use global query interface (or create new one if model params differ)
        if request.model != "gpt-3.5-turbo" or request.temperature != 0.0:
            # Create new instance if different model/temperature requested
            q_interface = NaturalLanguageQuery(model=request.model, temperature=request.temperature)
        else:
            q_interface = query_interface
        
        # Execute the query
        result, error = q_interface.execute(request.query)
        
        # Check for errors
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        if not result.get("success"):
            error_msg = result.get("error", "Query execution failed")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Return successful response
        return QueryResponse(
            success=result.get("success", False),
            data=result.get("data", []),
            count=result.get("count", 0),
            structured_query=result.get("structured_query", {}),
            user_query=result.get("user_query", request.query),
            metadata=result.get("metadata"),
            summary=result.get("summary"),
            error=result.get("error"),
            message=result.get("message")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

