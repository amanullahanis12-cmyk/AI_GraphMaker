"""Display utilities"""
import streamlit as st
import pandas as pd
from typing import Dict
from collections import defaultdict

def display_conversion_summary(summary: Dict):
    if not summary.get('converted_columns'):
        return
    
    type_groups = defaultdict(list)
    for col_info in summary['converted_columns']:
        type_groups[col_info['type']].append(col_info)
    
    icons = {'percentage': '📊', 'money': '💰', 'integer': '🔢', 'decimal': '🔣'}
    for col_type, columns in type_groups.items():
        with st.expander(f"{icons.get(col_type, '📈')} {col_type.capitalize()} ({len(columns)} columns)"):
            for col in columns:
                st.markdown(f"**{col['name']}** - {col.get('success_rate', 'Converted')}")