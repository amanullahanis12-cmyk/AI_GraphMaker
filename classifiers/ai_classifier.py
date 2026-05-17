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
        columns_info = [{'name': col, 'samples': df[col].dropna().head(3).tolist()} for col in df.columns]
        prompt = f"Classify each column as percentage/money/integer/decimal/text. Return JSON.\nColumns: {columns_info}"
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": "Return ONLY valid JSON."}, {"role": "user", "content": prompt}],
                model=self.MODEL_NAME, temperature=0.1, max_tokens=500
            )
            return self._parse_response(response.choices[0].message.content, df)
        except:
            return {col: 'text' for col in df.columns}
    
    def _parse_response(self, response: str, df: pd.DataFrame) -> Dict[str, str]:
        response = re.sub(r'```json\s*|```\s*', '', response.strip())
        try:
            types = json.loads(response)
            return {col: types.get(col, 'text') for col in df.columns}
        except:
            return {col: 'text' for col in df.columns}