"""Optimized graph execution utilities"""
import re
import builtins
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.basedatatypes import BaseFigure
    PLOTLY_OK = True
except:
    PLOTLY_OK = False
    BaseFigure = None

# Compile regex once for speed
CODE_CLEANER = re.compile(r'```python\s*|```\s*')
IMPORT_CHECK = re.compile(r'^(import|from)\s+')
DATAFRAME_CREATION = re.compile(r'pd\.DataFrame\(|df\s*=\s*\{|\bdf\s*=\s*pd\.|\bnew_df\s*=|\.reset_index\(\)|\.nlargest\(|\.groupby\(.*\)\.\w+\(\)')

def clean_ai_code(code: str, mode: str = 'plotly') -> str:
    """Fast code cleaning with pre-compiled regex"""
    code = CODE_CLEANER.sub('', code)
    lines = []
    for line in code.split('\n'):
        stripped = line.strip()
        # Skip imports and dataframe creation/modification
        if IMPORT_CHECK.match(stripped):
            continue
        if DATAFRAME_CREATION.search(stripped):
            continue
        # Skip variable assignments that aren't 'fig'
        if '=' in stripped and not stripped.startswith('fig'):
            if any(x in stripped for x in ['df', 'data', 'top_', 'new_', '_df']):
                continue
        lines.append(line)
    
    cleaned = '\n'.join(lines).strip()
    return cleaned or ("fig = px.scatter(title='No valid code generated')" if mode == 'plotly' else "plt.figure()\nplt.show()")

def execute_plotly_code(code: str, df: pd.DataFrame):
    """Execute Plotly code with minimal overhead"""
    if not PLOTLY_OK:
        return False, None, "Plotly not installed"
    
    # Restricted builtins
    safe_builtins = {k: v for k, v in builtins.__dict__.items() 
                     if k not in ['open', 'exec', 'eval', '__import__', 'compile', 'breakpoint']}
    
    try:
        scope = {
            '__builtins__': safe_builtins, 
            'df': df, 
            'pd': pd, 
            'px': px, 
            'go': go,
            'plt': plt,
            'np': __import__('numpy')
        }
        exec(code, scope)
        fig = scope.get('fig')
        if fig and (BaseFigure and isinstance(fig, BaseFigure) or hasattr(fig, 'to_html')):
            return True, fig, None
        return False, None, "No valid figure created. Make sure to assign your plot to a variable named 'fig'"
    except Exception as e:
        return False, None, str(e)

def execute_matplotlib_code(code: str, df: pd.DataFrame):
    """Execute matplotlib code with cleanup"""
    safe_builtins = {k: v for k, v in builtins.__dict__.items() 
                     if k not in ['open', 'exec', 'eval', '__import__', 'compile', 'breakpoint']}
    
    try:
        plt.clf()
        plt.close('all')
        scope = {
            '__builtins__': safe_builtins, 
            'df': df, 
            'plt': plt, 
            'pd': pd, 
            'np': __import__('numpy'),
            'sns': __import__('seaborn')
        }
        exec(code, scope)
        if plt.get_fignums():
            fig = plt.gcf()
            return True, fig, None
        return False, None, "No plot created"
    except Exception as e:
        plt.clf()
        return False, None, str(e)

def prepare_ai_prompt(df: pd.DataFrame, prompt: str, use_plotly: bool) -> str:
    """Generate concise prompt for AI with accurate column names"""
    # Get actual column names
    columns = list(df.columns)
    
    # Identify numeric and categorical columns
    numeric_cols = [c for c in columns if pd.api.types.is_numeric_dtype(df[c])]
    categorical_cols = [c for c in columns if not pd.api.types.is_numeric_dtype(df[c])]
    
    # Show sample data
    sample_data = df.head(5).to_string()
    
    # Create examples using actual columns
    example_x = categorical_cols[0] if categorical_cols else (numeric_cols[0] if numeric_cols else columns[0])
    example_y = numeric_cols[0] if numeric_cols else (columns[0] if columns else 'value')
    
    if use_plotly:
        example_code = f"""fig = px.bar(df, x='{example_x}', y='{example_y}', title='{example_y} by {example_x}')
fig.update_layout(template='plotly_white')"""
    else:
        example_code = f"""plt.figure(figsize=(10,6))
plt.bar(df['{example_x}'], df['{example_y}'])
plt.xlabel('{example_x}')
plt.ylabel('{example_y}')
plt.title('{example_y} by {example_x}')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()"""
    
    return f"""
╔════════════════════════════════════════════════════════════════╗
║                    CRITICAL RULES - READ FIRST                 ║
╠════════════════════════════════════════════════════════════════╣
║ 1. USE ONLY the existing 'df' dataframe - DO NOT create new ones ║
║ 2. DO NOT use .groupby().nlargest() or .reset_index()         ║
║ 3. DO NOT assign variables except 'fig'                       ║
║ 4. Use column names EXACTLY as shown below                    ║
║ 5. Column names are CASE-SENSITIVE                            ║
╚════════════════════════════════════════════════════════════════╝

EXACT COLUMN NAMES IN YOUR DATAFRAME:
{chr(10).join([f'   • "{col}"' for col in columns])}

NUMERIC COLUMNS (use for y-axis, values):
{chr(10).join([f'   • "{col}"' for col in numeric_cols]) if numeric_cols else '   • None'}

CATEGORY/TEXT COLUMNS (use for x-axis, groups):
{chr(10).join([f'   • "{col}"' for col in categorical_cols]) if categorical_cols else '   • None'}

SAMPLE DATA (first 5 rows):
{sample_data}

USER REQUEST: {prompt}

CORRECT EXAMPLE using your actual columns:
{example_code}

WRONG PATTERNS TO AVOID:
❌ top_five = df.groupby('category')['value'].nlargest(5).reset_index()
❌ new_df = df[df['col'] > 10]
❌ result = df.groupby('col').sum()
❌ x='name' (unless 'name' is actually a column name)
✅ fig = px.bar(df, x='{example_x}', y='{example_y}')

Generate ONLY Python code. No imports. No markdown. No dataframe creation.
{"Assign final plot to variable named 'fig'" if use_plotly else "Use plt.show() at the end"}
USE THE EXACT COLUMN NAMES SHOWN ABOVE.
"""