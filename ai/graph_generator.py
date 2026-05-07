"""
AI-powered graph generation using Groq
"""

import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from groq import Groq
from typing import Tuple, Optional
import streamlit as st

from security.code_validator import SecureCodeValidator


class SecureGraphGenerator:
    """Generates and executes graph code safely"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.validator = SecureCodeValidator()
    
    def generate_code(self, user_request: str, df: pd.DataFrame, context: str = "") -> str:
        """Generate visualization code using LLM"""
        
        # Sanitize user input
        sanitized_request = SecureCodeValidator.sanitize_prompt(user_request)
        
        # Prepare dataframe info
        df_info = {
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'shape': df.shape,
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns)
        }
        
        # Build prompt
        prompt = f"""
        VERY IMPORTANT: The dataframe 'df' already exists and is loaded with data.
        DO NOT create a new dataframe. DO NOT use pd.DataFrame() or df = {{}}.
        Use the existing variable 'df' which already contains the data.
        
        DATASET INFORMATION:
        - Shape: {df_info['shape']}
        - Columns: {', '.join(df_info['columns'])}
        - Numeric columns: {', '.join(df_info['numeric_columns'])}
        - Categorical columns: {', '.join(df_info['categorical_columns'])}
        
        USER REQUEST: {sanitized_request}
        
        PREVIOUS CONTEXT: {context}
        
        REQUIREMENTS:
        1. Use ONLY the existing 'df' variable
        2. Use matplotlib.pyplot as plt and seaborn as sns
        3. Create a clear, well-labeled visualization
        4. Handle data type conversions automatically
        5. Add proper titles, labels, and legends
        6. Use plt.tight_layout() for clean display
        7. Add plt.show() at the end
        8. Return ONLY the Python code, no explanations
        9. DO NOT include any markdown formatting
        
        GENERATE PYTHON CODE:
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a Python data visualization expert. Return ONLY executable Python code. NEVER create a new dataframe. ALWAYS use the existing 'df' variable."},
                    {"role": "user", "content": prompt}
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.3,
                max_tokens=2000
            )
            
            generated_code = response.choices[0].message.content
            
            # Clean code (remove markdown formatting if present)
            generated_code = re.sub(r'```python\n?', '', generated_code)
            generated_code = re.sub(r'```\n?', '', generated_code)
            
            return generated_code
            
        except Exception as e:
            return f"# Error generating code: {str(e)}\n# Please try a different request"
    
    def execute_code_safely(self, code: str, df: pd.DataFrame) -> Tuple[bool, str, Optional[plt.Figure]]:
        """Execute generated code in a safe environment"""
        
        # Validate code
        valid, msg = self.validator.check_dangerous_patterns(code)
        if not valid:
            return False, msg, None
        
        valid, msg = self.validator.validate_ast(code)
        if not valid:
            return False, msg, None
        
        # Prepare safe execution environment
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'range': range,
                'abs': abs,
                'min': min,
                'max': max,
                'sum': sum,
                'round': round,
            },
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'df': df.copy(),  # Work on copy to prevent modification
        }
        
        # Remove dangerous builtins
        dangerous_builtins = ['open', 'exec', 'eval', '__import__', 'compile', 
                             'globals', 'locals', 'getattr', 'setattr', 'delattr',
                             'input', 'raw_input', '__loader__', '__spec__', 'breakpoint']
        
        for dangerous in dangerous_builtins:
            safe_globals['__builtins__'].pop(dangerous, None)
        
        try:
            # Create a clean figure
            plt.clf()
            plt.close('all')
            
            # Execute code
            exec(code, safe_globals, {})
            
            # Get current figure
            fig = plt.gcf() if plt.get_fignums() else None
            
            return True, "Code executed successfully", fig
            
        except Exception as e:
            plt.clf()
            return False, f"Execution error: {str(e)}", None