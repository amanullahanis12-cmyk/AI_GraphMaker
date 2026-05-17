"""Graph utilities for safe execution"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import io
import builtins

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.basedatatypes import BaseFigure
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    BaseFigure = None

def clean_ai_code(code: str, mode: str = 'plotly') -> str:
    code = re.sub(r'```python\s*|```\s*', '', code)
    lines = [line for line in code.split('\n') 
             if not line.strip().startswith(('import ', 'from ')) 
             and 'pd.DataFrame' not in line]
    cleaned = '\n'.join(lines)
    return cleaned if cleaned.strip() else ("fig = px.scatter(title='No valid code')" if mode == 'plotly' else "plt.figure()\nplt.show()")

def execute_plotly_code(code: str, df: pd.DataFrame):
    if not PLOTLY_AVAILABLE:
        return False, None, "Plotly not installed"
    
    try:
        safe_globals = {
            '__builtins__': {k: v for k, v in builtins.__dict__.items() if k not in ['open', 'exec', 'eval']},
            'df': df, 'pd': pd, 'np': np, 'px': px, 'go': go
        }
        exec(code, safe_globals)
        fig = safe_globals.get('fig')
        if fig and (BaseFigure and isinstance(fig, BaseFigure) or hasattr(fig, 'to_html')):
            return True, fig, None
        return False, None, "No valid figure created"
    except Exception as e:
        return False, None, str(e)

def execute_and_display(code: str, df: pd.DataFrame):
    try:
        plt.clf()
        plt.close('all')
        safe_globals = {
            '__builtins__': {k: v for k, v in builtins.__dict__.items() if k not in ['open', 'exec', 'eval']},
            'df': df, 'plt': plt, 'sns': sns, 'pd': pd, 'np': np
        }
        exec(code, safe_globals)
        if plt.get_fignums():
            fig = plt.gcf()
            st.pyplot(fig, use_container_width=True)
            return True, "Success", fig
        return False, "No plot created", None
    except Exception as e:
        return False, str(e), None

def prepare_ai_prompt(df, user_prompt, use_plotly=True):
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    examples = """
EXAMPLE: "Bar chart of sales by region"
fig = px.bar(df, x="Region", y="Sales", title="Sales by Region")
fig.update_layout(template="plotly_white")
""" if use_plotly else """
EXAMPLE: "Bar chart of sales by region"
plt.figure(figsize=(12,6))
df.groupby("Region")["Sales"].mean().plot(kind="bar")
plt.title("Sales by Region")
plt.tight_layout()
plt.show()
"""
    
    return f"""
CRITICAL: 'df' is already loaded with converted numeric values.
Columns: {', '.join(df.columns)}
Numeric: {', '.join(numeric_cols)}
Categorical: {', '.join(categorical_cols)}
User request: {user_prompt}
{examples}
Generate ONLY Python code (no imports, no markdown). Use existing 'df' variable.
{"Assign plot to variable 'fig'." if use_plotly else ""}
"""