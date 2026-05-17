# tutorio/utils/graph_utils.py
"""
Graph utilities for safe execution and display
"""

import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import io
import builtins


def clean_ai_code(code: str) -> str:
    """
    Clean AI-generated code for graph mode only.
    Removes markdown fences, import statements, dataframe creation,
    and lines that modify df unless they are plotting commands.
    """
    # Remove markdown fences
    code = re.sub(r'```python\s*', '', code)
    code = re.sub(r'```\s*', '', code)
    
    lines = code.split('\n')
    clean_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip import statements
        if stripped.startswith('import ') or stripped.startswith('from '):
            continue
        
        # Skip dataframe creation
        if 'pd.DataFrame' in stripped or 'df = {' in stripped:
            continue
        
        # Skip lines that modify df unless they also contain plt or sns
        if re.match(r'^df\[', stripped) and '=' in stripped and not any(x in stripped for x in ['plt.', 'sns.']):
            continue
        
        clean_lines.append(line)
    
    cleaned = '\n'.join(clean_lines)
    
    if not cleaned.strip():
        cleaned = "plt.figure(figsize=(10,6))\nplt.text(0.5,0.5,'No valid code',ha='center')\nplt.show()"
    
    return cleaned


def execute_and_display(code: str, df: pd.DataFrame):
    """Safely execute code and display graph"""
    try:
        plt.clf()
        plt.close('all')
        
        safe_builtins = builtins.__dict__.copy()
        dangerous = [
            'open', 'exec', 'eval', '__import__', 'compile',
            'globals', 'locals', 'getattr', 'setattr', 'delattr',
            'input', 'raw_input', '__loader__', '__spec__', 'breakpoint',
            '__builtins__', 'help', 'license', 'copyright', 'credits'
        ]
        for key in dangerous:
            safe_builtins.pop(key, None)
        
        safe_globals = {
            '__builtins__': safe_builtins,
            'df': df,
            'plt': plt,
            'sns': sns,
            'pd': pd,
            'np': np,
        }
        
        exec(code, safe_globals)
        
        if plt.get_fignums():
            fig = plt.gcf()
            st.pyplot(fig)
            return True, "Graph generated successfully!", fig
        else:
            return False, "No plot created", None
            
    except Exception as e:
        return False, f"Error: {str(e)}", None


def create_downloadable_image(fig):
    """Create downloadable image buffer"""
    if fig is None:
        return None
    try:
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        return buffer
    except:
        return None


def prepare_ai_prompt(df, user_prompt):
    """Prepare prompt for AI with converted data info"""
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    prompt = f"""
CRITICAL: The dataframe 'df' is already loaded and CONVERTED.
- All numbers (4.5B, $2.5M, 62k, 15%) are already converted to numeric values
- Use the columns as they are - NO conversion needed

COLUMNS:
{chr(10).join([f'- {col}: {df[col].dtype}' for col in df.columns])}

NUMERIC COLUMNS (use for calculations/axes): {', '.join(numeric_cols) if numeric_cols else 'None'}

CATEGORICAL COLUMNS (use for grouping): {', '.join(categorical_cols) if categorical_cols else 'None'}

USER REQUEST: {user_prompt}

Generate ONLY Python code (no imports, no markdown):
- Start with: plt.figure(figsize=(12,6))
- Use df[column] directly
- Add labels and titles
- End with: plt.tight_layout(); plt.show()
"""
    return prompt