"""
Utility helper functions
"""

import streamlit as st
import pandas as pd
from typing import Optional


def display_data_preview(df: pd.DataFrame, rows: int = 10):
    """Display data preview in an expander"""
    with st.expander("🔍 Data Preview"):
        st.dataframe(df.head(rows), use_container_width=True)
        st.caption(f"Showing first {rows} rows of {len(df)} total rows")


def display_dataset_info(df: pd.DataFrame):
    """Display dataset information summary"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        numeric_cols = len(df.select_dtypes(include=['number']).columns)
        st.metric("Numeric Columns", numeric_cols)


def format_code_for_display(code: str) -> str:
    """Format code for better display in Streamlit"""
    # Remove excessive whitespace
    lines = [line.rstrip() for line in code.split('\n')]
    return '\n'.join(lines)