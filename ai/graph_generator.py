"""AI-powered graph generation using Groq"""
import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from groq import Groq
from typing import Tuple, Optional
from security.code_validator import SecureCodeValidator

class SecureGraphGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.validator = SecureCodeValidator()
    
    def generate_code(self, user_request: str, df: pd.DataFrame, context: str = "") -> str:
        sanitized_request = SecureCodeValidator.sanitize_prompt(user_request)
        df_info = {
            'columns': list(df.columns),
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns)
        }
        
        prompt = f"""
        CRITICAL: The dataframe 'df' already exists. DO NOT create a new dataframe.
        Columns: {', '.join(df_info['columns'])}
        Numeric: {', '.join(df_info['numeric_columns'])}
        Categorical: {', '.join(df_info['categorical_columns'])}
        User request: {sanitized_request}
        Context: {context}
        
        Generate Python code using matplotlib and seaborn. Use plt.show() at the end.
        Return ONLY the Python code, no explanations.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a Python visualization expert. Return ONLY executable Python code. Use existing 'df' variable."},
                    {"role": "user", "content": prompt}
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.3,
                max_tokens=2000
            )
            return re.sub(r'```python\n?|```\n?', '', response.choices[0].message.content)
        except Exception as e:
            return f"# Error: {str(e)}"
    
    def execute_code_safely(self, code: str, df: pd.DataFrame) -> Tuple[bool, str, Optional[plt.Figure]]:
        valid, msg = self.validator.check_dangerous_patterns(code)
        if not valid:
            return False, msg, None
        
        valid, msg = self.validator.validate_ast(code)
        if not valid:
            return False, msg, None
        
        safe_globals = {
            '__builtins__': {k: v for k, v in __builtins__.__dict__.items() if k not in ['open', 'exec', 'eval', '__import__']},
            'pd': pd, 'np': np, 'plt': plt, 'sns': sns, 'df': df.copy()
        }
        
        try:
            plt.clf()
            plt.close('all')
            exec(code, safe_globals, {})
            fig = plt.gcf() if plt.get_fignums() else None
            return True, "Success", fig
        except Exception as e:
            return False, f"Error: {str(e)}", None