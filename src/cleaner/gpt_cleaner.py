"""
GPT-based name cleaning module.
Uses OpenAI GPT to suggest cleaned display names.
"""
import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class GPTCleaner:
    """Uses GPT to clean and standardize names."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0):
        """
        Initialize GPT cleaner.
        
        Args:
            model: OpenAI model to use
            temperature: Model temperature (0 = deterministic)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
    
    def clean_item_names(self, name_group: List[str], category_name: Optional[str] = None) -> str:
        """
        Suggest a cleaned display name for a group of similar item names.
        
        Args:
            name_group: List of similar item names (e.g., ["Hash Browns", "Hashbrowns"])
            category_name: Optional category name for context
            
        Returns:
            Suggested cleaned display name
        """
        names_str = ", ".join([f'"{name}"' for name in name_group])
        
        context = ""
        if category_name:
            context = f" These items are in the '{category_name}' category."
        
        prompt = f"""Given these variations of the same restaurant menu item, suggest a single cleaned, standardized display name.

Names: [{names_str}]{context}

Rules:
1. Fix spelling errors (e.g., "coffe" → "Coffee", "expresso" → "Espresso")
2. Standardize capitalization (use Title Case for proper nouns)
3. Choose the most common/standard spelling
4. Return ONLY the cleaned name, no explanations or quotes

Cleaned display name:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that standardizes restaurant menu item names. Return only the cleaned name, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=100
            )
            
            cleaned_name = response.choices[0].message.content.strip()
            # Remove quotes if present
            cleaned_name = cleaned_name.strip('"\'')
            
            return cleaned_name
            
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")
    
    def clean_variation_names(self, name_group: List[str], item_name: Optional[str] = None) -> Dict[str, str]:
        """
        Suggest cleaned display names for a group of item variation names.
        
        Args:
            name_group: List of variation names for the same item (e.g., ["6 piece", "6pc", "reg", "Regular"])
            item_name: Optional item name for context
            
        Returns:
            Dictionary mapping original names to cleaned display names
        """
        names_str = ", ".join([f'"{name}"' for name in name_group])
        
        context = ""
        if item_name:
            context = f" These are variations of '{item_name}'."
        
        prompt = f"""Given these variation names for the same menu item, suggest cleaned, standardized display names for each.

Variation names: [{names_str}]{context}

Rules:
1. Fix spelling and abbreviations (e.g., "reg" → "Regular", "dbl" → "Double")
2. Standardize formats (e.g., "6 piece", "6pc", "6 pcs" → "6 pc")
3. Use consistent capitalization (e.g., "Regular", "Large", "Small")
4. Return a JSON object mapping each original name to its cleaned version

Return ONLY valid JSON in this format:
{{"original_name1": "cleaned_name1", "original_name2": "cleaned_name2", ...}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that standardizes restaurant menu item variation names. Return only valid JSON mapping original names to cleaned names."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            cleaned_mapping = json.loads(result_text)
            
            # Ensure all names in the group are in the mapping
            result = {}
            for name in name_group:
                if name in cleaned_mapping:
                    result[name] = cleaned_mapping[name]
                else:
                    # Fallback: use the name as-is if not in mapping
                    result[name] = name
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")

