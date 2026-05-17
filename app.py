"""AI Data Analyst - Powered by Groq AI (Llama 4 Scout)"""
import streamlit as st
import pandas as pd
import hashlib
from pathlib import Path
from datetime import datetime
from groq import Groq
import tempfile

from utils.graph_utils import clean_ai_code, execute_and_display, prepare_ai_prompt, execute_plotly_code
from converters.data_converter import DataFrameProcessor
from security.csv_validator import CSVValidator
from chat.history_manager import ChatHistoryManager

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

def init_session_state():
    defaults = {
        'chat_history': [], 'df': None, 'original_df': None,
        'conversion_summary': None, 'groq_client': None, 'graph_cache': {}
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def generate_and_display_graph(df, user_prompt, use_plotly=True):
    try:
        if not st.session_state.groq_client:
            st.session_state.groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        df_hash = hashlib.md5(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()
        cache_key = f"{user_prompt}_{df_hash}_{use_plotly}"
        
        if cache_key in st.session_state.graph_cache:
            cleaned_code = st.session_state.graph_cache[cache_key]['code']
            st.info("♻️ Using cached graph")
        else:
            ai_prompt = prepare_ai_prompt(df, user_prompt, use_plotly)
            system_msg = ("You are a data visualization expert. Return ONLY Python code. "
                         "Always assign the final figure to a variable named 'fig'. "
                         "Use the existing 'df' DataFrame.") if use_plotly else (
                         "You are a data visualization expert. Return ONLY Python code using matplotlib. "
                         "Use plt.figure(), then plt.plot/bar/hist, and end with plt.show().")
            
            response = st.session_state.groq_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": ai_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            cleaned_code = clean_ai_code(response.choices[0].message.content, 'plotly' if use_plotly else 'matplotlib')
            st.session_state.graph_cache[cache_key] = {'code': cleaned_code, 'plotly': use_plotly}
        
        with st.expander("📝 Generated Code"):
            st.code(cleaned_code, language="python")
        
        if use_plotly:
            success, fig, error = execute_plotly_code(cleaned_code, df)
            if success:
                st.plotly_chart(fig, use_container_width=True)
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
                        fig.write_html(tmp.name)
                    with open(tmp.name, 'rb') as f:
                        st.download_button("📥 Download HTML", f.read(), f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html", "text/html")
                    Path(tmp.name).unlink()
                except:
                    st.download_button("📥 Download HTML", fig.to_html(), f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html", "text/html")
                ChatHistoryManager.add_message('assistant', "Graph generated!", {'type': 'graph', 'code': cleaned_code, 'plotly': True})
            else:
                st.error(f"❌ {error}")
        else:
            success, msg, fig = execute_and_display(cleaned_code, df)
            if success:
                st.success(f"✅ {msg}")
                if fig:
                    buf = fig.savefig(format='png', bbox_inches='tight')
                    st.download_button("📥 Download PNG", buf, f"graph.png", "image/png")
                ChatHistoryManager.add_message('assistant', msg, {'type': 'graph', 'code': cleaned_code, 'plotly': False})
            else:
                st.error(f"❌ {msg}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.set_page_config(page_title="AI Data Analyst", layout="wide")
st.markdown("""
<style>.stButton>button{width:100%;background:#ff4b4b;color:white;border-radius:8px}</style>
""", unsafe_allow_html=True)

init_session_state()
ChatHistoryManager.initialize()

st.title("🤖 AI Data Analyst")
st.markdown("### Upload CSV → Describe Graph → Get Visualizations")

with st.sidebar:
    st.header("📁 Data Upload")
    uploaded_file = st.file_uploader("Choose CSV", type="csv")
    if uploaded_file:
        try:
            if CSVValidator.validate_csv_content(uploaded_file.getvalue())[0]:
                original_df = pd.read_csv(uploaded_file)
                converted_df, summary = DataFrameProcessor.auto_convert(original_df, st.secrets.get("GROQ_API_KEY"))
                st.session_state.df, st.session_state.original_df, st.session_state.conversion_summary = converted_df, original_df, summary
                st.success(f"✅ {len(converted_df):,} rows, {len(summary.get('converted_columns', []))} columns converted")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if st.button("🗑️ Clear Cache"):
        st.session_state.graph_cache = {}
        st.rerun()

if st.session_state.df is not None:
    with st.expander("📊 Data Preview", expanded=False):
        st.dataframe(st.session_state.df.head())
    
    st.subheader("📊 Describe Your Graph")
    user_prompt = st.text_area("What graph do you want?", height=100)
    use_plotly = st.checkbox("📈 Interactive (Plotly)", value=True)
    
    if st.button("🎨 Generate Graph", type="primary"):
        if user_prompt:
            generate_and_display_graph(st.session_state.df, user_prompt, use_plotly)
        else:
            st.warning("Please describe what graph you want!")
else:
    st.info("👈 Upload a CSV file to get started")