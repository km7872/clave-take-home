"""
GPT-based name cleaning module.
Uses OpenAI GPT to suggest cleaned display names.
"""
import os
import json
from typing import List, Optional, Dict, Tuple
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class GPTCleaner:
    """Uses GPT to clean and standardize names."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
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
    
    def clean_item_names(self, name_groups: List[List[str]], category_name: Optional[str] = None) -> List[str]:
        """
        Suggest cleaned display names for multiple groups of similar item names in a single API call.
        
        Args:
            name_groups: List of lists of similar item names (e.g., [["Hash Browns", "Hashbrowns"], ["Coffee", "Coffe"]])
            category_name: Optional category name for context
            
        Returns:
            List of cleaned display names, one for each name group (in the same order)
        """
        if not name_groups:
            return []
        
        # Format groups for the prompt
        groups_formatted = []
        for i, name_group in enumerate(name_groups):
            names_str = ", ".join([f'"{name}"' for name in name_group])
            groups_formatted.append(f"Group {i+1}: [{names_str}]")
        
        groups_text = "\n".join(groups_formatted)
        
        context = ""
        if category_name:
            context = f" These items are in the '{category_name}' category."
        
        prompt = f"""You are given {len(name_groups)} groups of similar restaurant menu item names. For each group, suggest a single cleaned, standardized display name.

{groups_text}{context}

Rules:
1. Fix spelling errors (e.g., "coffe" → "Coffee", "expresso" → "Espresso")
2. Standardize capitalization (use Title Case for proper nouns)
3. Choose the most common/standard spelling
4. Return a JSON object with keys "group1", "group2", etc., mapping to the cleaned name for each group
5. Return ONLY valid JSON, no explanations or additional text

Return format (JSON):
{{"group1": "CleanedName1", "group2": "CleanedName2", "group3": "CleanedName3", ...}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that standardizes restaurant menu item names. Return only valid JSON with group keys mapping to cleaned names."
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
            
            # Try to fix common JSON issues
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                # Remove ```json or ``` markers
                lines = result_text.split('\n')
                if lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                result_text = '\n'.join(lines).strip()
            
            # Try to parse JSON
            try:
                result_json = json.loads(result_text)
            except json.JSONDecodeError as json_error:
                # Log the problematic response for debugging
                error_msg = f"Failed to parse LLM response as JSON: {str(json_error)}\n"
                error_msg += f"Response length: {len(result_text)} characters\n"
                error_msg += f"First 500 chars: {result_text[:500]}\n"
                error_msg += f"Last 500 chars: {result_text[-500:] if len(result_text) > 500 else result_text}"
                raise ValueError(error_msg)
            
            # Extract cleaned names in order (group1, group2, etc.)
            cleaned_names = []
            for i in range(len(name_groups)):
                key = f"group{i+1}"
                if key not in result_json:
                    raise ValueError(f"Missing key '{key}' in GPT response. Got keys: {list(result_json.keys())}")
                cleaned_name = result_json[key]
                # Handle if it's not a string (shouldn't happen, but be safe)
                if isinstance(cleaned_name, str):
                    cleaned_name = cleaned_name.strip().strip('"\'')
                else:
                    cleaned_name = str(cleaned_name).strip()
                cleaned_names.append(cleaned_name)
            
            return cleaned_names
            
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")
    
    def clean_variation_names(self, variation_groups: List[Tuple[List[str], str]]) -> List[Dict[str, str]]:
        """
        Suggest cleaned display names for multiple groups of item variation names in a single API call.
        
        Args:
            variation_groups: List of tuples, each containing (variation_names, item_name)
                           e.g., [(["6 piece", "6pc"], "Burger"), (["reg", "Regular"], "Fries")]
            
        Returns:
            List of dictionaries, each mapping original variation names to cleaned display names
            (one dict per group, in the same order as input)
        """
        if not variation_groups:
            return []
        
        # Format groups for the prompt
        groups_formatted = []
        all_variation_names = []
        for i, (variation_names, item_name) in enumerate(variation_groups):
            names_str = ", ".join([f'"{name}"' for name in variation_names])
            groups_formatted.append(f"Group {i+1} (variations of '{item_name}'): [{names_str}]")
            all_variation_names.extend(variation_names)
        
        groups_text = "\n".join(groups_formatted)
        
        prompt = f"""You are given {len(variation_groups)} groups of variation names for different menu items. For each group, suggest cleaned, standardized display names for each variation.

{groups_text}

Rules:
1. Fix spelling and abbreviations (e.g., "reg" → "Regular", "dbl" → "Double")
2. Standardize formats (e.g., "6 piece", "6pc", "6 pcs" → "6 pc")
3. Use consistent capitalization (e.g., "Regular", "Large", "Small")
4. Return ONLY valid JSON - no markdown, no explanations, no code blocks
5. Properly escape all quotes and special characters in JSON strings
6. Use double quotes for all JSON keys and string values

Return format (valid JSON only):
{{"group1": {{"original_name1": "cleaned_name1", "original_name2": "cleaned_name2"}}, "group2": {{"original_name3": "cleaned_name3"}}, ...}}

IMPORTANT: Return ONLY the JSON object, nothing else. Ensure all strings are properly escaped."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that standardizes restaurant menu item variation names. Return only valid JSON with group keys mapping to objects of original->cleaned name mappings."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=min(4000, 100 + len(variation_groups) * 50)  # Scale with number of groups, max 4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Check if response was truncated (ends with incomplete JSON)
            if not result_text.rstrip().endswith('}'):
                # Response might be truncated - try to detect and handle
                # Check if it ends mid-string or mid-object
                if result_text.rstrip().endswith('"') or '"' in result_text[-20:]:
                    # Likely truncated - try to complete the JSON
                    # Find the last complete group
                    last_complete_brace = result_text.rfind('}')
                    if last_complete_brace > 0:
                        # Try to extract what we can
                        partial_json = result_text[:last_complete_brace + 1]
                        # Try to close the outer object
                        open_braces = partial_json.count('{')
                        close_braces = partial_json.count('}')
                        if open_braces > close_braces:
                            # Add missing closing braces
                            partial_json += '}' * (open_braces - close_braces)
                        result_text = partial_json
            
            # Try to fix common JSON issues
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                # Remove ```json or ``` markers
                lines = result_text.split('\n')
                if lines[0].strip().startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                result_text = '\n'.join(lines).strip()
            
            # Try to parse JSON
            try:
                result_json = json.loads(result_text)
            except json.JSONDecodeError as json_error:
                # Log the problematic response for debugging
                error_msg = f"Failed to parse LLM response as JSON: {str(json_error)}\n"
                error_msg += f"Response length: {len(result_text)} characters\n"
                error_msg += f"Number of groups expected: {len(variation_groups)}\n"
                error_msg += f"First 500 chars: {result_text[:500]}\n"
                error_msg += f"Last 500 chars: {result_text[-500:] if len(result_text) > 500 else result_text}"
                raise ValueError(error_msg)
            
            # Extract cleaned mappings for each group
            cleaned_mappings = []
            for i, (variation_names, item_name) in enumerate(variation_groups):
                key = f"group{i+1}"
                if key not in result_json:
                    # If response was truncated, use original names as fallback for missing groups
                    print(f"Warning: Missing key '{key}' in GPT response (response may have been truncated). Using original names.")
                    result = {name: name for name in variation_names}
                    cleaned_mappings.append(result)
                    continue
                
                group_mapping = result_json[key]
                if not isinstance(group_mapping, dict):
                    raise ValueError(f"Expected dict for '{key}', got {type(group_mapping)}")
                
                # Ensure all names in the group are in the mapping
                result = {}
                for name in variation_names:
                    if name in group_mapping:
                        cleaned = group_mapping[name]
                        # Handle if it's not a string (shouldn't happen, but be safe)
                        if isinstance(cleaned, str):
                            result[name] = cleaned.strip().strip('"\'')
                        else:
                            result[name] = str(cleaned).strip()
                    else:
                        # Fallback: use the name as-is if not in mapping
                        result[name] = name
                
                cleaned_mappings.append(result)
            
            return cleaned_mappings
            
        except json.JSONDecodeError as e:
            # This should be caught above, but keep as fallback
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            if 'result_text' in locals():
                error_msg += f"\nResponse preview: {result_text[:500]}"
            raise ValueError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")

