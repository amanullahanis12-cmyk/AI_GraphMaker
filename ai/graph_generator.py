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
        You are a secure data visualization expert. Generate ONLY Python code for the following request.
        
        DATASET INFORMATION:
        - Shape: {df_info['shape']}
        - Columns: {', '.join(df_info['columns'])}
        - Numeric columns: {', '.join(df_info['numeric_columns'])}
        - Categorical columns: {', '.join(df_info['categorical_columns'])}
        
        USER REQUEST: {sanitized_request}
        
        PREVIOUS CONTEXT: {context}
        
        REQUIREMENTS:
        1. Use ONLY the following imports: pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
        2. The dataframe variable is ALWAYS 'df'
        3. Use plt.figure(figsize=(10, 6)) for each plot
        4. Add proper titles, labels, and legends
        5. Use plt.tight_layout()
        6. Return ONLY the code, no explanations
        7. DO NOT use: exec, eval, open, file operations, system commands
        8. Handle missing data gracefully
        9. Add comments to explain the visualization
        
        GENERATE PYTHON CODE:
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a Python data visualization expert. Return ONLY executable Python code."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
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
            'np': __import__('numpy'),
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