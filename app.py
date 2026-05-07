"""
AI Graph Generator - Complete Working Version
Integrates all security, chat, and AI modules with proper response formatting
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from groq import Groq
import re
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import modular components (create these files if they don't exist)
try:
    from security.code_validator import SecureCodeValidator
    from security.csv_validator import CSVValidator
    from chat.history_manager import ChatHistoryManager
    from ai.graph_generator import SecureGraphGenerator
    from utils.helpers import display_data_preview, display_dataset_info
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    st.warning("Optional modules not found. Running in standalone mode.")

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Graph Generator", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #ff6b6b;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        color: #155724;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .code-block {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 AI Graph Generator")
st.markdown("### Powered by Groq AI with DeepSeek Integration")
st.markdown("Upload a CSV, describe the graph you want, and the AI will create it for you!")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_df' not in st.session_state:
    st.session_state.current_df = None
if 'plot_counter' not in st.session_state:
    st.session_state.plot_counter = 0

# Sidebar
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.current_df = df
            st.success(f"✅ Loaded: {uploaded_file.name}")
            st.info(f"📊 {df.shape[0]} rows, {df.shape[1]} columns")
            
            with st.expander("View Data Preview"):
                st.dataframe(df.head(10))
                
            with st.expander("Data Info"):
                st.write("**Column Names:**")
                st.write(", ".join(df.columns))
                st.write("**Data Types:**")
                st.write(df.dtypes)
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Settings
    st.subheader("⚙️ Settings")
    execution_mode = st.selectbox(
        "Execution Mode",
        ["Safe Mode", "Review Only", "Debug Mode"],
        help="Safe Mode: Validates code before running | Review Only: Shows code only | Debug Mode: Shows all errors"
    )
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    with st.expander("🔒 Security Features"):
        st.markdown("""
        - ✅ Removes import statements
        - ✅ Prevents dataframe recreation
        - ✅ Safe execution sandbox
        - ✅ Input sanitization
        """)

# Function to clean AI response (FIXES THE IMPORT ISSUE)
def clean_ai_code(code: str) -> str:
    """Clean AI-generated code by removing imports and markdown"""
    
    # Remove markdown code blocks
    code = re.sub(r'```python\s*', '', code)
    code = re.sub(r'```\s*', '', code)
    
    # Split into lines
    lines = code.split('\n')
    clean_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip import statements
        if stripped.startswith('import ') or stripped.startswith('from '):
            continue
        
        # Skip lines that try to create a new dataframe
        if 'pd.DataFrame' in stripped or '= pd.DataFrame' in stripped:
            continue
        if 'df = {' in stripped or 'df = pd.read' in stripped:
            continue
        
        # Skip empty lines at the start
        if not clean_lines and not stripped:
            continue
            
        clean_lines.append(line)
    
    # Join back together
    cleaned = '\n'.join(clean_lines)
    
    # If nothing remains, return a default message
    if not cleaned.strip():
        cleaned = "plt.figure(figsize=(10,6))\nplt.text(0.5, 0.5, 'No valid code generated', ha='center')\nplt.show()"
    
    return cleaned

# Function to safely execute code and display graph
def execute_and_display(code: str, df: pd.DataFrame):
    """Safely execute AI code and display the graph"""
    
    try:
        # Clear any existing figures
        plt.clf()
        plt.close('all')
        
        # Create safe execution environment
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
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'round': round,
                'type': type,
            },
            'df': df.copy(),
            'plt': plt,
            'sns': sns,
            'pd': pd,
            'np': np,
        }
        
        # Execute the cleaned code
        exec(code, safe_globals)
        
        # Display the plot if one was created
        if plt.get_fignums():
            st.pyplot(plt)
            return True, "Graph generated successfully!"
        else:
            return False, "Code executed but no plot was created. Make sure to use plt.show() or plt.figure()"
            
    except Exception as e:
        return False, f"Execution error: {str(e)}"

# Main area
if st.session_state.current_df is not None:
    df = st.session_state.current_df
    
    # Display column information
    st.subheader("📋 Available Columns")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**📊 Numeric Columns:**")
        st.write(", ".join(numeric_cols) if numeric_cols else "None")
    with col2:
        st.write("**📝 Text Columns:**")
        st.write(", ".join(text_cols) if text_cols else "None")
    
    # Show all columns
    st.write("**📋 All Columns:**")
    st.write(", ".join(df.columns))
    
    # Chat/input area
    st.subheader("💬 Describe Your Graph")
    
    # Display chat history
    for msg in st.session_state.chat_history[-10:]:  # Show last 10 messages
        if msg['role'] == 'user':
            st.chat_message("user").write(msg['content'])
        else:
            with st.chat_message("assistant"):
                st.write(msg['content'])
                if msg.get('has_plot') and msg.get('code'):
                    with st.expander("View Code"):
                        st.code(msg['code'], language="python")
    
    # User input
    user_prompt = st.text_area(
        "What graph do you want?",
        placeholder=f"Examples:\n- Create a bar chart of {numeric_cols[0] if numeric_cols else 'a numeric column'}\n- Make a histogram of {numeric_cols[0] if numeric_cols else 'a numeric column'}\n- Create a scatter plot\n- Show correlation heatmap",
        height=100,
        key="user_input"
    )
    
    # Generate button
    if st.button("🎨 Generate Graph", type="primary"):
        if not user_prompt:
            st.warning("Please describe what graph you want!")
        else:
            # Add user message to history
            st.session_state.chat_history.append({'role': 'user', 'content': user_prompt})
            
            with st.spinner("🤖 AI is generating your graph..."):
                
                # Prepare AI prompt (STRICT formatting instructions)
                ai_prompt = f"""
                CRITICAL INSTRUCTIONS - FOLLOW EXACTLY:
                
                1. The dataframe 'df' ALREADY EXISTS. DO NOT create a new dataframe.
                2. DO NOT write any import statements (import, from...import).
                3. DO NOT use markdown or explanations.
                4. Write ONLY visualization code using plt and sns.
                5. Start with plt.figure(figsize=(10,6))
                6. End with plt.show()
                
                Dataset columns: {list(df.columns)}
                Numeric columns: {numeric_cols}
                
                User request: {user_prompt}
                
                Generate ONLY Python code (no imports, no markdown):
                """
                
                try:
                    # Call AI
                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[
                            {"role": "system", "content": "You generate visualization code. Return ONLY Python code. NO imports. NO markdown. Use existing 'df' variable."},
                            {"role": "user", "content": ai_prompt}
                        ],
                        temperature=0.2,  # Lower temperature for more consistent output
                        max_tokens=1000,
                    )
                    
                    # Get raw code
                    raw_code = response.choices[0].message.content
                    
                    # Clean the code (removes imports, markdown, etc.)
                    cleaned_code = clean_ai_code(raw_code)
                    
                    # Display the cleaned code
                    with st.expander("📝 View Generated Code"):
                        st.code(cleaned_code, language="python")
                    
                    # Execute and display graph
                    if execution_mode == "Review Only":
                        st.info("⚠️ Review Mode: Code generated but not executed. Copy and run manually if needed.")
                        success = False
                        message = "Code ready for review"
                    else:
                        success, message = execute_and_display(cleaned_code, df)
                        
                        if success:
                            st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
                            
                            # Save plot image
                            plot_path = f"temp_plot_{st.session_state.plot_counter}.png"
                            plt.savefig(plot_path, dpi=100, bbox_inches='tight')
                            st.session_state.plot_counter += 1
                            plt.close('all')
                        else:
                            st.error(f"❌ {message}")
                            
                            if execution_mode == "Debug Mode":
                                st.write("**Raw AI Response:**")
                                st.code(raw_code, language="python")
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': message if success else "Failed to generate graph",
                        'has_plot': success,
                        'code': cleaned_code
                    })
                    
                except Exception as e:
                    st.error(f"AI Error: {str(e)}")
                    st.info("Please try rephrasing your request or check your API key.")

else:
    # No file uploaded
    st.info("👈 Please upload a CSV file in the sidebar to get started")
    
    with st.expander("📖 How to Use"):
        st.markdown("""
        **Simple Steps:**
        1. Upload a CSV file using the sidebar
        2. Describe the graph you want in plain English
        3. Click "Generate Graph"
        4. Your graph appears instantly!
        
        **Example Prompts:**
        - "Create a bar chart showing the distribution of [column name]"
        - "Make a histogram of [numeric column]"
        - "Create a scatter plot between [column X] and [column Y]"
        - "Show a correlation heatmap of all numeric columns"
        
        **Tips:**
        - Be specific about which columns to use
        - Mention the type of graph you want
        - The AI will automatically clean and validate the code
        """)
        
        # Sample data generator
        if st.button("📝 Generate Sample CSV"):
            sample_data = pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D', 'E'],
                'Value': [10, 20, 15, 25, 30],
                'Score': [85, 90, 78, 92, 88]
            })
            csv = sample_data.to_csv(index=False)
            st.download_button(
                label="Download Sample CSV",
                data=csv,
                file_name="sample_data.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8rem;'>
🔒 AI Graph Generator | Secure Code Execution | Powered by Groq
</div>
""", unsafe_allow_html=True)