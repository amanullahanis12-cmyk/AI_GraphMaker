"""AI-powered column classification"""
import pandas as pd
import json
import re
from typing import Dict, List
from groq import Groq

class AITypeClassifier:
    VALID_TYPES = {'percentage', 'money', 'integer', 'decimal', 'text'}
    MODEL_NAME = "llama-3.1-8b-instant"
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def classify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Use AI to classify columns"""
        columns_info = []
        for col in df.columns:
            sample_values = df[col].dropna().head(5).tolist()
            columns_info.append({
                'name': col,
                'dtype': str(df[col].dtype),
                'samples': [str(v)[:50] for v in sample_values]
            })
        
        prompt = self._build_prompt(columns_info)
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a data classification expert. Return ONLY valid JSON. No explanations."},
                    {"role": "user", "content": prompt}
                ],
                model=self.MODEL_NAME,
                temperature=0.1,
                max_tokens=500
            )
            return self._parse_response(response.choices[0].message.content, df)
        except Exception as e:
            # Fallback to keyword classification
            return {col: 'text' for col in df.columns}
    
    def _build_prompt(self, columns_info: List[Dict]) -> str:
        """Build classification prompt"""
        columns_list = []
        for info in columns_info:
            columns_list.append(
                f'- "{info["name"]}" (type: {info["dtype"]}, samples: {info["samples"]})'
            )
        
        return f"""
Classify each column into one type based on name and sample values.

TYPES:
- "percentage" - Percentages, rates, ratios (look for %, percent, rate, ratio)
- "money" - Currency values (look for $, €, £, salary, revenue, cost)
- "integer" - Whole numbers (counts, quantities)
- "decimal" - Other decimal numbers
- "text" - Non-numeric data

Columns:
{chr(10).join(columns_list)}

Return ONLY JSON: {{"column_name": "type", ...}}
"""
    
    def _parse_response(self, response: str, df: pd.DataFrame) -> Dict[str, str]:
        """Parse AI response"""
        response = re.sub(r'```json\s*|```\s*', '', response.strip())
        
        try:
            types = json.loads(response)
            # Validate types
            validated = {}
            for col in df.columns:
                col_type = types.get(col, 'text')
                validated[col] = col_type if col_type in self.VALID_TYPES else 'text'
            return validated
        except:
            return {col: 'text' for col in df.columns}