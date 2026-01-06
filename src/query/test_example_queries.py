"""
Test script for example queries from EXAMPLE_QUERIES.md.
Tests which queries work and which don't.
"""
from src.query.query_interface import NaturalLanguageQuery
import json


def test_query(query: str, query_interface: NaturalLanguageQuery):
    """Test a single query and return success status."""
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print('='*80)
    
    try:
        result, error = query_interface.execute(query)
        
        success = result.get("success", False)
        count = result.get("count", 0)
        has_error = error is not None or result.get("error") is not None
        
        if success and not has_error and count > 0:
            status = "[OK] WORKING"
            print(f"Status: {status}")
            print(f"Count: {count}")
            print(f"Intent: {result.get('structured_query', {}).get('intent', 'N/A')}")
            if result.get('metadata'):
                print(f"Has metadata: Yes")
            if result.get('summary'):
                print(f"Has summary: Yes")
        elif success and count == 0:
            status = "[WARN] NO DATA"
            print(f"Status: {status}")
            print(f"Message: {result.get('message', 'No data found')}")
        else:
            status = "[FAIL] FAILED"
            print(f"Status: {status}")
            if error:
                print(f"Error: {error}")
            if result.get('error'):
                print(f"Query Error: {result.get('error')}")
        
        return {
            "query": query,
            "status": status,
            "success": success,
            "count": count,
            "error": error or result.get('error')
        }
    except Exception as e:
        print(f"Status: [ERR] EXCEPTION")
        print(f"Exception: {str(e)}")
        return {
            "query": query,
            "status": "[ERR] EXCEPTION",
            "success": False,
            "count": 0,
            "error": str(e)
        }


def main():
    """Test all example queries."""
    query_interface = NaturalLanguageQuery()
    
    queries = [
        # Basic Queries
        # "Show me total sales by location",
        "What was the revenue yesterday?",
        # "List the top 10 selling items",
        
        # # Comparison Queries
        # "Compare sales between Downtown and Airport",
        # "Show me Downtown vs University revenue",
        # "Which location had the highest sales?",
        
        # # Time-Based Queries
        # "Show me sales for January 2nd",
        # "What were hourly sales on the 3rd?",
        # "Graph daily revenue for the first week",
        
        # # Product Analysis
        # "What are the top selling items at the Mall?",
        # "Show me beverage sales across all locations",
        # "Which category generates the most revenue?",
        
        # # Channel Analysis
        # "Compare delivery vs dine-in revenue",
        # "How much came from DoorDash?",
        # "Show me takeout orders by location",
        
        # # Advanced Queries
        # "Show me peak hours for each location",
        # "What's the average order value by channel?",
        # "Graph the trend of delivery orders over time",
        # "Which payment methods are most popular?",
    ]
    
    results = []
    for query in queries:
        result = test_query(query, query_interface)
        results.append(result)
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    
    working = [r for r in results if "WORKING" in r["status"]]
    no_data = [r for r in results if "NO DATA" in r["status"]]
    failed = [r for r in results if "FAILED" in r["status"]]
    exceptions = [r for r in results if "EXCEPTION" in r["status"]]
    
    print(f"\n[OK] Working: {len(working)}/{len(queries)}")
    for r in working:
        print(f"  - {r['query']}")
    
    print(f"\n[WARN] No Data: {len(no_data)}/{len(queries)}")
    for r in no_data:
        print(f"  - {r['query']}")
    
    print(f"\n[FAIL] Failed: {len(failed)}/{len(queries)}")
    for r in failed:
        print(f"  - {r['query']}")
        if r['error']:
            print(f"    Error: {r['error']}")
    
    print(f"\n[ERR] Exceptions: {len(exceptions)}/{len(queries)}")
    for r in exceptions:
        print(f"  - {r['query']}")
        if r['error']:
            print(f"    Error: {r['error']}")


if __name__ == '__main__':
    main()

