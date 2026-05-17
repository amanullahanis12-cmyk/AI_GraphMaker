# tutorio/app.py
"""
AI Data Analyst – DeepSeek Coded | Powered by Groq AI
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from groq import Groq
import sys
from pathlib import Path
from datetime import datetime
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import modular components
from utils.graph_utils import clean_ai_code, execute_and_display, create_downloadable_image, prepare_ai_prompt
from converters.data_converter import DataFrameProcessor
from classifiers import ColumnClassifier
from security.csv_validator import CSVValidator
from chat.history_manager import ChatHistoryManager

# ============================================================================
# Function Definitions
# ============================================================================

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'chat_history': [],
        'df': None,
        'original_df': None,
        'conversion_summary': None,
        'groq_client': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def handle_graph_mode(df: pd.DataFrame):
    """Handle graph mode UI and logic"""
    st.subheader("📊 Describe Your Graph")
    
    user_prompt = st.text_area(
        "What graph do you want?",
        placeholder="Examples:\n- Bar chart of salary by department\n- Histogram of revenue\n- Scatter plot between revenue and profit",
        height=100
    )
    
    if st.button("🎨 Generate Graph", type="primary", use_container_width=True):
        if not user_prompt:
            st.warning("Please describe what graph you want!")
            return
        
        ChatHistoryManager.add_message('user', f"📊 {user_prompt}")
        
        with st.spinner("🤖 Generating graph..."):
            generate_and_display_graph(df, user_prompt)


def generate_and_display_graph(df: pd.DataFrame, user_prompt: str):
    """Generate and display a graph based on user prompt"""
    try:
        if not st.session_state.groq_client:
            st.session_state.groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        ai_prompt = prepare_ai_prompt(df, user_prompt)
        
        response = st.session_state.groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are a data visualization expert. Return ONLY Python code. No imports. No markdown."},
                {"role": "user", "content": ai_prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        
        raw_code = response.choices[0].message.content
        cleaned_code = clean_ai_code(raw_code)  # mode removed
        
        with st.expander("📝 Generated Code"):
            st.code(cleaned_code, language="python")
        
        success, message, fig = execute_and_display(cleaned_code, df)
        
        if success:
            st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                img_buffer = create_downloadable_image(fig)
                if img_buffer:
                    st.download_button(
                        "📥 Download PNG",
                        img_buffer,
                        f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "image/png",
                        use_container_width=True
                    )
            with col_b:
                st.download_button(
                    "📝 Download Code",
                    cleaned_code,
                    f"code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                    "text/plain",
                    use_container_width=True
                )
            
            ChatHistoryManager.add_message('assistant', message, {
                'type': 'graph',
                'has_plot': True,
                'code': cleaned_code
            })
        else:
            st.error(f"❌ {message}")
            
    except Exception as e:
        st.error(f"Error generating graph: {str(e)}")


def display_chat_history():
    """Display conversation history"""
    history = ChatHistoryManager.get_history()
    
    if history:
        st.markdown("---")
        st.subheader("💬 Conversation History")
        
        for msg in history[-10:]:
            if msg['role'] == 'user':
                st.chat_message("user").write(msg['content'])
            else:
                with st.chat_message("assistant"):
                    if msg.get('metadata', {}).get('has_plot'):
                        st.write(msg['content'])
                        if msg['metadata'].get('code'):
                            with st.expander("🔧 View Code"):
                                st.code(msg['metadata']['code'], language="python")


def show_welcome_screen():
    """Welcome screen when no file is uploaded"""
    st.info("👈 **Upload a CSV file to get started**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Graph 
        Create visualizations:
        - Bar charts
        - Histograms
        - Scatter plots
        - Heatmaps
        """)
    
    with col2:
        st.markdown("""
        ### 🧠 Smart Detection
        Automatic type inference:
        - Percentages → 0.8500
        - Money → $1,234.56
        - Counts → 123
        """)

# ============================================================================
# Page Configuration and UI Setup
# ============================================================================
st.set_page_config(
    page_title="AI Data Analyst – DeepSeek Coded | Groq AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #ff6b6b;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Initialize app state
init_session_state()
ChatHistoryManager.initialize()

# ============================================================================
# Header
# ============================================================================
st.title("🤖 AI Data Analyst")
st.markdown("### 🧠 DeepSeek Coded · ⚡ Powered by Groq AI")
st.markdown("Upload a CSV, then describe the graph you want.")

# ============================================================================
# Sidebar – Minimal
# ============================================================================
with st.sidebar:
    st.header("📁 Data Upload")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file:
        try:
            content = uploaded_file.getvalue()
            valid, msg = CSVValidator.validate_csv_content(content)
            if not valid:
                st.error(f"⚠️ Security check failed: {msg}")
                st.stop()
            
            with st.spinner("🔄 Loading and analyzing data types..."):
                original_df = pd.read_csv(uploaded_file)
                st.session_state.original_df = original_df
                
                api_key = st.secrets.get("GROQ_API_KEY")
                converted_df, summary = DataFrameProcessor.auto_convert(original_df, api_key)
                
                st.session_state.df = converted_df
                st.session_state.conversion_summary = summary
            
            st.success(f"✅ {uploaded_file.name} · {converted_df.shape[0]:,} rows · {len(summary.get('converted_columns', []))} columns converted")
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    st.markdown("---")
    
    st.subheader("⚙️ Settings")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ============================================================================
# Main Content Area
# ============================================================================
if st.session_state.df is not None:
    df = st.session_state.df
    summary = st.session_state.conversion_summary
    
    # Compact data preview (collapsed by default)
    with st.expander("📊 View Data & Types", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Data**")
            st.dataframe(st.session_state.original_df.head(5), use_container_width=True)
        with col2:
            st.markdown("**Converted Data**")
            st.dataframe(df.head(5), use_container_width=True)
        
        if summary:
            type_data = []
            for col in df.columns:
                type_data.append({
                    'Column': col,
                    'Type': str(df[col].dtype),
                    'Classification': summary.get('column_types', {}).get(col, 'unknown')
                })
            st.markdown("**Column Types After Conversion:**")
            st.dataframe(pd.DataFrame(type_data), use_container_width=True)
    
    # Only Graph Mode
    handle_graph_mode(df)
    
    # Display chat history
    display_chat_history()

else:
    show_welcome_screen()

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8rem;'>
🧠 DeepSeek Coded · ⚡ Powered by Groq AI
</div>
""", unsafe_allow_html=True)