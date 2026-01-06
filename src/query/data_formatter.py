"""
LLM-based data formatter that filters and formats API responses based on user intent.
"""
import json
import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class DataFormatter:
    """
    Uses LLM to format and filter API response data based on user query.
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Initialize the data formatter.
        
        Args:
            model: OpenAI model to use
            temperature: Model temperature
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
    
    def format_response(self, api_data: List[Dict], user_query: str, structured_query: Dict) -> List[Dict]:
        """
        Format and filter API response data based on user query.
        
        Args:
            api_data: Raw data from API
            user_query: Original user query
            structured_query: Structured query that was used
            
        Returns:
            Filtered and formatted data list
        """
        if not api_data:
            return []
        
        # Create prompt for LLM to filter/format data
        prompt = self._build_prompt(api_data, user_query, structured_query)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data formatter. You filter and format API response data based on user queries. Return ONLY valid JSON with a 'data' array containing the filtered records. Match the structure of the input data but filter to only include what the user asked for."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return result.get("data", api_data)
            
        except (json.JSONDecodeError, Exception) as e:
            # If LLM formatting fails, return original data
            return api_data
    
    def _build_prompt(self, api_data: List[Dict], user_query: str, structured_query: Dict) -> str:
        """
        Build prompt for LLM to format data.
        
        Args:
            api_data: Raw data from API
            user_query: Original user query
            structured_query: Structured query
            
        Returns:
            Formatted prompt string
        """
        # Sample first few records
        sample_data = api_data[:5] if len(api_data) > 5 else api_data
        
        prompt = f"""Filter and format the following API response data based on the user's query.

USER QUERY: {user_query}

STRUCTURED QUERY INTENT: {structured_query.get('intent', '')}

API DATA (showing {len(sample_data)} of {len(api_data)} records):
{json.dumps(sample_data, indent=2)}

INSTRUCTIONS:
1. Filter the data to match what the user specifically asked for in their query
2. If the user asked for specific locations/items/values, only include those
3. Keep the same data structure but remove records that don't match the user's request
4. If filtering would result in empty data, return the original data instead

Return JSON in this format:
{{
  "data": [filtered records array]
}}

Return ONLY the JSON object, no additional text:"""
        
        return prompt

