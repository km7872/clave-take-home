"""
Test script for natural language query interface.
"""
from src.query.query_interface import NaturalLanguageQuery


def main():
    """Test natural language queries."""
    query_interface = NaturalLanguageQuery()
    
    test_queries = [
        # "Show me all locations",
        "Show me revenue of Downtown and Airport locations",
        # "What were my top 5 selling products?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)
        
        result, error = query_interface.execute(query)
        
        print(f"\nStructured Query:")
        import json
        print(json.dumps(result.get("structured_query", {}), indent=2))
        
        if error:
            print(f"\nError: {error}")
            if not result.get('success'):
                print(f"Query Error Details: {result.get('error', 'Unknown error')}")
            continue
        
        print(f"\nResults:")
        print(f"  Success: {result.get('success')}")
        if not result.get('success'):
            print(f"  Error: {result.get('error', 'Unknown error')}")
        print(f"  Count: {result.get('count')}")
        print(f"  Data (first 3 records):")
        data = result.get("data", [])
        for i, record in enumerate(data[:3]):
            print(f"    {i+1}. {record}")


if __name__ == '__main__':
    main()

