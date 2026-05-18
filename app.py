"""AI Data Analyst - Optimized with Caching & Performance"""
import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from groq import Groq
import io
import re

from utils.graph_utils import execute_plotly_code, execute_matplotlib_code, prepare_ai_prompt, clean_ai_code
from converters.data_converter import DataFrameProcessor
from security.csv_validator import CSVValidator
from chat.history_manager import ChatHistoryManager

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

# Cache Groq client initialization
@st.cache_resource
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# Cache DataFrame hash for faster comparisons
@st.cache_data
def get_df_hash(df: pd.DataFrame) -> str:
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()

def init_session():
    defaults = {
        'df': None, 'original_df': None, 'summary': None,
        'fig': None, 'code': None, 'use_plotly': True,
        'history': [], 'code_cache': {}
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)

def validate_and_fix_code(code: str, df: pd.DataFrame) -> str:
    """Remove any problematic patterns from code"""
    # Remove groupby operations that create new dataframes
    patterns_to_remove = [
        r'[\w_]+\s*=\s*df\.groupby\([^)]+\.[\w]+\([^)]*\)[^;]*;?',
        r'[\w_]+\s*=\s*df\[[^\]]+\][\s\S]*?\.(nlargest|nsmallest|reset_index)\([^)]*\)[^;]*;?',
        r'[\w_]+\s*=\s*df\.copy\(\)[^;]*;?',
        r'[\w_]+\s*=\s*df\[[^\]]+\][^;]*;?',
    ]
    
    for pattern in patterns_to_remove:
        code = re.sub(pattern, '', code, flags=re.MULTILINE)
    
    # Remove any lines that assign variables (except fig)
    lines = []
    for line in code.split('\n'):
        stripped = line.strip()
        if '=' in stripped and not stripped.startswith('fig'):
            # Keep if it's just a simple filter for plotting
            if not any(x in stripped for x in ['groupby', 'nlargest', 'reset_index', 'copy']):
                lines.append(line)
        else:
            lines.append(line)
    
    return '\n'.join(lines)

def generate_graph(df: pd.DataFrame, prompt: str, use_plotly: bool):
    """Generate and cache graph"""
    client = get_groq_client()
    df_hash = get_df_hash(df)
    cache_key = f"{prompt}_{df_hash}_{use_plotly}"
    
    # Get or generate code
    if cache_key not in st.session_state.code_cache:
        ai_prompt = prepare_ai_prompt(df, prompt, use_plotly)
        system_msg = """You are a data visualization expert. Return ONLY Python code.
CRITICAL RULES:
1. NEVER create new dataframes (no df = ..., no new_df = ...)
2. NEVER use .groupby().nlargest() or .reset_index()
3. ONLY use the existing 'df' variable
4. Use column names EXACTLY as shown in the prompt
5. Keep plots simple - direct from the original dataframe
6. Always assign to variable 'fig' for Plotly"""

        if not use_plotly:
            system_msg = system_msg.replace("'fig'", "plt.show()")
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": ai_prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent output
                max_tokens=1000   # Reduced tokens
            )
            raw_code = response.choices[0].message.content
            clean_code = clean_ai_code(raw_code, 'plotly' if use_plotly else 'matplotlib')
            # Additional validation
            clean_code = validate_and_fix_code(clean_code, df)
            st.session_state.code_cache[cache_key] = clean_code
        except Exception as e:
            st.error(f"AI Error: {str(e)}")
            return False
    
    code = st.session_state.code_cache[cache_key]
    
    with st.expander("📝 Generated Code"):
        st.code(code, language="python")
    
    # Execute and store
    if use_plotly:
        success, fig, err = execute_plotly_code(code, df)
    else:
        success, fig, err = execute_matplotlib_code(code, df)
    
    if success:
        st.session_state.fig, st.session_state.code, st.session_state.use_plotly = fig, code, use_plotly
        return True
    
    # Provide helpful error message
    st.error(f"❌ {err}")
    st.info("💡 Tip: Try a simpler request. Example: 'Bar chart of Net_Assets by category'")
    
    # Show available columns to help user
    with st.expander("📊 Available Columns (use these exact names)"):
        st.write("**Column names you can use in your request:**")
        for col in df.columns:
            dtype = "🔢 numeric" if pd.api.types.is_numeric_dtype(df[col]) else "📝 text"
            sample_val = df[col].iloc[0] if len(df) > 0 else "N/A"
            st.write(f"- `{col}` ({dtype}) - example: {sample_val}")
    
    return False

def display_downloads():
    """Persistent download buttons"""
    if st.session_state.fig is None:
        return
    
    st.markdown("---")
    st.subheader("📥 Download")
    
    cols = st.columns(3)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if st.session_state.use_plotly:
        with cols[0]:
            try:
                img = st.session_state.fig.to_image(format="png", width=800, height=500, scale=2)
                st.download_button("📸 PNG", img, f"graph_{ts}.png", "image/png", use_container_width=True)
            except:
                st.info("💡 `pip install kaleido` for PNG export")
        
        with cols[1]:
            st.download_button("📥 HTML", st.session_state.fig.to_html(), f"graph_{ts}.html", "text/html", use_container_width=True)
        
        with cols[2]:
            st.download_button("📝 Code", st.session_state.code, f"code_{ts}.py", "text/plain", use_container_width=True)
    else:
        with cols[0]:
            buf = io.BytesIO()
            st.session_state.fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            st.download_button("📸 PNG", buf.getvalue(), f"graph_{ts}.png", "image/png", use_container_width=True)
        
        with cols[1]:
            buf = io.BytesIO()
            st.session_state.fig.savefig(buf, format='pdf', bbox_inches='tight')
            st.download_button("📄 PDF", buf.getvalue(), f"graph_{ts}.pdf", "application/pdf", use_container_width=True)
        
        with cols[2]:
            st.download_button("📝 Code", st.session_state.code, f"code_{ts}.py", "text/plain", use_container_width=True)

# UI Setup
st.set_page_config("AI Data Analyst", "🤖", "wide")
st.title("🤖 AI Data Analyst")
st.caption("Upload CSV → Describe Graph → Get Insights")

init_session()
ChatHistoryManager.initialize()

# Sidebar
with st.sidebar:
    file = st.file_uploader("📁 Upload CSV", type="csv")
    
    if file:
        if CSVValidator.validate_csv_content(file.getvalue())[0]:
            df = pd.read_csv(file)
            with st.spinner("Converting..."):
                converted, summary = DataFrameProcessor.auto_convert(df, st.secrets.get("GROQ_API_KEY"))
                st.session_state.df, st.session_state.original_df, st.session_state.summary = converted, df, summary
            st.success(f"✅ {len(converted):,} rows, {len(summary.get('converted_columns', []))} converted")
    
    if st.button("🗑️ Clear", use_container_width=True):
        for key in ['fig', 'code', 'code_cache']:
            st.session_state.pop(key, None)
        st.rerun()

# Main content
if st.session_state.df is not None:
    # Graph generation
    st.markdown("### 💬 Describe Your Graph")
    st.caption("Be specific with column names. Example: 'Bar chart showing Net_Assets by category'")
    
    prompt = st.text_area("", height=68, 
                         placeholder="Example: Bar chart of Net_Assets by category | Show me a scatter plot (use existing column names)")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        use_plotly = st.checkbox("📈 Interactive", True)
    with col2:
        if st.button("🎨 Generate", type="primary", use_container_width=True) and prompt:
            with st.spinner("🤖 Generating..."):
                if generate_graph(st.session_state.df, prompt, use_plotly):
                    ChatHistoryManager.add_message('user', prompt)
                    ChatHistoryManager.add_message('assistant', "Graph ready", {'code': st.session_state.code})
    
    # Display current graph
    if st.session_state.fig:
        st.markdown("### 📈 Result")
        if st.session_state.use_plotly:
            st.plotly_chart(st.session_state.fig, use_container_width=True)
        else:
            st.pyplot(st.session_state.fig, use_container_width=True)
    
    display_downloads()
else:
    st.info("👈 Upload a CSV to begin")

st.markdown("---")
st.caption("⚡ Tip: Mention specific column names from your data for best results")