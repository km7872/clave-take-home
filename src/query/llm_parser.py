"""
LLM-based query parser.
Converts natural language queries to structured JSON queries.
"""
import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from src.query.schema import get_schema_json, get_schema_summary

load_dotenv()


class LLMQueryParser:
    """
    Parses natural language queries into structured JSON query objects using GPT.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Initialize the LLM parser.
        
        Args:
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: Model temperature (0 = deterministic, higher = creative)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.schema = get_schema_json()
        self.schema_summary = get_schema_summary()
    
    def parse_query(self, user_query: str) -> Dict:
        """
        Parse natural language query into structured JSON query.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Structured query dictionary
        """
        prompt = self._build_prompt(user_query)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a query builder for a restaurant analytics database. You convert natural language queries into structured JSON query objects. Always return valid JSON only, no additional text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            structured_query = json.loads(result_text)
            
            return structured_query
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")
    
    def _build_prompt(self, user_query: str) -> str:
        """
        Build the prompt for the LLM.
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Formatted prompt string
        """
        schema_text = get_schema_summary()
        
        # Use .format() instead of f-string to avoid nested brace issues with JSON examples
        prompt = """Convert the following natural language query into a structured JSON query object.

{schema_text}

IMPORTANT INSTRUCTIONS:
1. Use ONLY the tables and columns listed above
2. For sales/revenue queries, use the "total_money" column from orders table or "total_amount" from order_details
3. For "sales" queries, clarify: if asking for revenue use "total_money", if asking for count use COUNT of orders
4. Location names are: Downtown, Airport, Mall Location, University
5. When joining tables, use the relationships specified in the schema
6. For items and item_variations tables, ALWAYS use "display_name" instead of "name" when selecting, grouping by, or filtering by product names (this ensures products with the same display name are treated as one)
7. Return ONLY valid JSON, no explanations

QUERY FORMAT (return JSON in this exact structure):
{{
    "intent": "string describing the query intent",
    "tables": ["table1", "table2"],
    "select": ["column1", "aggregation(column2) as alias"],
    "aggregations": ["SUM", "COUNT", "AVG", "MAX", "MIN"],  // optional
    "joins": [
        {{"type": "inner", "table": "table2", "on": "table1.foreign_key = table2.primary_key"}}
    ],
    "filters": {{
        "column_name": {{"operator": "eq|in|gte|lte|gt|lt|like", "value": "value" or ["value1", "value2"]}}
    }},
    "group_by": ["column1", "column2"],
    "order_by": {{"column": "column_name", "direction": "asc|desc"}},
    "limit": null or number,
    "visualization": {{
        "type": "bar_chart|line_chart|pie_chart|table|metric_card|text",
        "x_axis": "column_name or null",
        "y_axis": "column_name or null"
    }}
}}

VISUALIZATION TYPE RULES:
- bar_chart: Comparisons, rankings, categories (e.g., revenue by location, top products)
- line_chart: Trends over time (e.g., revenue over time, hourly patterns)
- pie_chart: Part-to-whole relationships (e.g., payment methods, fulfillment types)
- table: Detailed data, multiple columns, lists
- metric_card: Single number/value (e.g., total revenue, average order value)
- text: Simple questions that need text response

EXAMPLES:

User Query: "Show me sales comparison between Downtown and Airport locations"
Response:
{{
  "intent": "sales_comparison_by_location",
  "tables": ["orders", "locations"],
  "select": [
    "locations.id",
    "locations.name",
    "SUM(orders.total_money) AS total_sales"
  ],
  "aggregations": ["SUM"],
  "joins": [
    {{
      "type": "inner",
      "table": "locations",
      "on": "orders.location_id = locations.id"
    }}
  ],
  "filters": {{
    "locations.name": {{
      "operator": "in",
      "value": ["Downtown", "Airport"]
    }}
  }},
  "group_by": ["locations.id", "locations.name"],
  "order_by": null,
  "limit": null,
  "visualization": {{
    "type": "bar_chart",
    "x_axis": "locations.name",
    "y_axis": "total_sales"
  }}
}}

User Query: "What were my top 5 selling products?"
Response:
{{
  "intent": "top_products",
  "tables": ["item_variations", "order_details"],
  "select": [
    "item_variations.display_name",
    "SUM(order_details.gross_amount) AS gross"
  ],
  "aggregations": ["SUM"],
  "joins": [
    {{
      "type": "inner",
      "table": "order_details",
      "on": "item_variations.id = order_details.itemvar_id"
    }}
  ],
  "filters": null,
  "group_by": ["item_variations.display_name"],
  "order_by": {{
    "column": "gross",
    "direction": "desc"
  }},
  "limit": 5,
  "visualization": {{
    "type": "bar_chart",
    "x_axis": "item_variations.display_name",
    "y_axis": "gross"
  }}
}}

Now convert this query:
{user_query}

Return ONLY the JSON object, no additional text:""".format(
            schema_text=schema_text,
            user_query=user_query
        )

        return prompt

