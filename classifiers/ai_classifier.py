# tutorio/classifiers/ai_classifier.py
"""
AI-powered column classification using Groq
"""

import pandas as pd
import json
import re
from typing import Dict, List
from groq import Groq


class AITypeClassifier:
    """Uses Groq AI to intelligently classify column data types"""
    
    VALID_TYPES = {'percentage', 'money', 'integer', 'decimal', 'text'}
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"  # Fast, efficient model
    
    def _prepare_column_info(self, df: pd.DataFrame) -> List[Dict]:
        """Prepare column information for AI analysis"""
        columns_info = []
        for col in df.columns:
            sample_values = df[col].dropna().head(3).tolist()
            columns_info.append({
                'name': col,
                'dtype': str(df[col].dtype),
                'samples': [str(v)[:50] for v in sample_values]  # Truncate long values
            })
        return columns_info
    
    def classify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Use AI to classify all columns based on their names and sample values.
        """
        columns_info = self._prepare_column_info(df)
        
        prompt = self._build_classification_prompt(columns_info)
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are a data classification expert. "
                            "Analyze column names and sample values to determine the correct data type. "
                            "Return ONLY valid JSON. No explanations."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=500
            )
            
            return self._parse_ai_response(response.choices[0].message.content, df)
            
        except Exception as e:
            raise Exception(f"AI classification failed: {str(e)}")
    
    def _build_classification_prompt(self, columns_info: List[Dict]) -> str:
        """Build the classification prompt for AI"""
        columns_list = []
        for info in columns_info:
            columns_list.append(
                f'- "{info["name"]}" (dtype: {info["dtype"]}, samples: {info["samples"]})'
            )
        
        return f"""
Classify each column into exactly ONE type based on its name and sample values.

AVAILABLE TYPES:
- "percentage" - Percentages, rates, ratios, margins, dependencies (should be 0-1 or 0-100)
- "money" - Monetary/currency values (salary, revenue, costs, compensation, assets, budgets)
- "integer" - Whole numbers/counts (employee count, population, quantity)
- "decimal" - Decimal numbers without specific category
- "text" - Non-numeric categorical/text data

CLASSIFICATION RULES:
1. Column names containing: percent, pct, rate, ratio, margin, dependency, share, growth → "percentage"
2. Column names containing: salary, revenue, cost, price, compensation, budget, expense, profit, loss, asset, liability, income, payment, earning, fee → "money"
3. Column names containing: count, number, employees, staff, people, population, quantity → "integer"
4. Sample values containing % → "percentage"
5. Sample values containing $, €, £, ¥ → "money"

COLUMNS:
{chr(10).join(columns_list)}

Return ONLY: {{"Column_Name": "type", ...}}
"""
    
    def _parse_ai_response(self, response_text: str, df: pd.DataFrame) -> Dict[str, str]:
        """Parse and validate AI response"""
        # Clean response
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        try:
            column_types = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                try:
                    column_types = json.loads(match.group())
                except:
                    raise Exception("Invalid JSON response from AI")
            else:
                raise Exception("No JSON found in AI response")
        
        # Validate and clean types
        validated_types = {}
        for col in df.columns:
            if col in column_types:
                col_type = column_types[col].lower().strip()
                validated_types[col] = col_type if col_type in self.VALID_TYPES else 'text'
            else:
                validated_types[col] = 'text'
        
        return validated_types
    
    def ensure_consistency(self, column_types: Dict[str, str]) -> Dict[str, str]:
        """
        Use AI to check for consistency issues and correct misclassifications.
        """
        # Group columns by type for analysis
        type_groups = {}
        for col, col_type in column_types.items():
            if col_type not in type_groups:
                type_groups[col_type] = []
            type_groups[col_type].append(col)
        
        prompt = f"""
Review these column classifications for consistency errors.

CURRENT CLASSIFICATION:
{json.dumps(column_types, indent=2)}

RULES:
1. ALL columns with "rate", "ratio", "percentage", "pct", "margin" in name MUST be "percentage"
2. ALL columns with "salary", "revenue", "cost", "compensation" in name MUST be "money"
3. ALL columns with "count", "number", "employees" in name MUST be "integer"
4. Related columns (sharing keywords) should have SAME type

Return ONLY JSON with corrections needed: {{"Column_Name": "corrected_type"}}
If no corrections needed, return: {{}}
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You check data type consistency. Return ONLY valid JSON with corrections."
                    },
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=300
            )
            
            corrections_text = response.choices[0].message.content.strip()
            corrections_text = re.sub(r'```json\s*', '', corrections_text)
            corrections_text = re.sub(r'```\s*', '', corrections_text)
            
            corrections = json.loads(corrections_text)
            
            # Apply corrections
            for col, corrected_type in corrections.items():
                if corrected_type.lower() in self.VALID_TYPES and col in column_types:
                    column_types[col] = corrected_type.lower()
            
            return column_types
            
        except:
            # If AI consistency check fails, use basic keyword rules
            return self._apply_basic_consistency(column_types)
    
    def _apply_basic_consistency(self, column_types: Dict[str, str]) -> Dict[str, str]:
        """Apply basic consistency rules as fallback"""
        for col in column_types:
            col_lower = col.lower()
            
            # Force percentage for rate/ratio columns
            if any(word in col_lower for word in ['rate', 'ratio', 'percent', 'pct', 'margin']):
                column_types[col] = 'percentage'
            
            # Force money for financial columns
            elif any(word in col_lower for word in ['salary', 'revenue', 'cost', 'compensation', 'budget', 'expense']):
                column_types[col] = 'money'
            
            # Force integer for count columns
            elif any(word in col_lower for word in ['count', 'number', 'employees', 'staff']):
                column_types[col] = 'integer'
        
        return column_types