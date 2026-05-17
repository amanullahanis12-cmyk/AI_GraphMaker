# tutorio/utils/display_utils.py
"""
Display utilities for Streamlit UI
"""

import streamlit as st
import pandas as pd
from typing import Dict
from collections import defaultdict


def display_conversion_summary(summary: Dict):
    """Display conversion summary with type grouping"""
    if not summary.get('converted_columns'):
        return
    
    # Show classification method
    method = summary.get('classification_method', 'keyword')
    if method == 'ai':
        st.success("🧠 AI-powered classification completed")
    else:
        st.info("📋 Keyword-based classification completed")
    
    # Group converted columns by type
    type_groups = defaultdict(list)
    for col_info in summary['converted_columns']:
        type_groups[col_info['type']].append(col_info)
    
    # Display by type
    type_icons = {
        'percentage': ('📊', 'Percentage Columns'),
        'money': ('💰', 'Money/Currency Columns'),
        'integer': ('🔢', 'Integer/Count Columns'),
        'decimal': ('🔣', 'Decimal Columns'),
        'numeric': ('📈', 'Numeric Columns')
    }
    
    for col_type, columns in type_groups.items():
        icon, label = type_icons.get(col_type, ('📈', f'{col_type.capitalize()} Columns'))
        
        with st.expander(f"{icon} {label} ({len(columns)} columns)", expanded=True):
            for col_info in columns:
                st.markdown(f"**{col_info['name']}**")
                st.caption(f"✓ {col_info['success_rate']} values converted")
                
                if col_info.get('examples'):
                    st.markdown("**Examples:**")
                    for ex in col_info['examples']:
                        st.markdown(f"• {ex}")
                st.markdown("---")


def display_data_quality_report(df: pd.DataFrame, summary: Dict):
    """Display data quality metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    
    with col2:
        st.metric("Total Columns", len(df.columns))
    
    with col3:
        converted = len(summary.get('converted_columns', []))
        st.metric("Converted Columns", converted)
    
    with col4:
        skipped = len(summary.get('skipped_columns', []))
        st.metric("Skipped Columns", skipped)