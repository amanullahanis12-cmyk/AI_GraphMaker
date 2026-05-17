"""Helper utilities"""
import streamlit as st
import pandas as pd

def display_data_preview(df: pd.DataFrame, rows: int = 10):
    with st.expander("🔍 Data Preview"):
        st.dataframe(df.head(rows), use_container_width=True)
        st.caption(f"Showing {rows} of {len(df)} rows")