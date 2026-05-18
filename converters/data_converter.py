"""Optimized data conversion with vectorized operations"""
import pandas as pd
import numpy as np
import re
from typing import Tuple, Dict, Optional
from functools import lru_cache
from classifiers import ColumnClassifier

class ValueParser:
    # Pre-compiled replacements for speed
    CURRENCY_CLEAN = str.maketrans('', '', '$€£¥₹,')
    SUFFIX_MAP = {'k': 1e3, 'K': 1e3, 'm': 1e6, 'M': 1e6, 'b': 1e9, 'B': 1e9, 't': 1e12, 'T': 1e12}
    
    @staticmethod
    @lru_cache(maxsize=10000)
    def parse_single(value, col_type: str):
        """Parse single value with caching"""
        if pd.isna(value) or value == '':
            return np.nan
        
        s = str(value).strip()
        
        # Handle parentheses for negative numbers
        if s.startswith('(') and s.endswith(')'):
            s = '-' + s[1:-1]
        
        # Remove currency symbols and commas
        has_pct = '%' in s
        s = s.translate(ValueParser.CURRENCY_CLEAN).replace('%', '').replace(',', '')
        
        # Check suffix
        mult = 1
        if s and s[-1] in ValueParser.SUFFIX_MAP:
            mult = ValueParser.SUFFIX_MAP[s[-1]]
            s = s[:-1]
        
        # Clean remaining
        s = re.sub(r'[^\d\.-]', '', s)
        
        if not s or s == '.':
            return np.nan
        
        try:
            val = float(s) * mult
            if has_pct or col_type == 'percentage':
                val = val / 100 if val > 1 else val
            if col_type == 'percentage':
                return round(val, 6)
            elif col_type == 'money':
                return round(val, 2)
            elif col_type == 'integer':
                return int(round(val))
            else:
                return round(val, 4)
        except:
            return np.nan
    
    @staticmethod
    def format_for_display(value: float, col_type: str) -> str:
        """Format for display"""
        if pd.isna(value):
            return 'N/A'
        if col_type == 'percentage':
            return f"{value*100:.1f}%"
        elif col_type == 'money':
            return f"${value:,.2f}"
        elif col_type == 'integer':
            return f"{int(value):,}"
        else:
            return f"{value:,.2f}"

class IntelligentDataConverter:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def convert_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Convert DataFrame with intelligent type detection"""
        converted = df.copy()
        summary = {
            'converted_columns': [],
            'skipped_columns': [],
            'column_types': {},
            'conversion_examples': {}
        }
        
        # Detect types efficiently
        for col in df.columns:
            col_lower = col.lower()
            
            # Keyword-based detection
            if any(k in col_lower for k in ['salary', 'revenue', 'cost', 'price', 'income', 'compensation', 'budget', 'asset']):
                col_type = 'money'
            elif any(k in col_lower for k in ['percent', 'pct', 'rate', 'margin', 'growth', 'share', 'ratio']):
                col_type = 'percentage'
            elif any(k in col_lower for k in ['count', 'number', 'employees', 'quantity', 'population', 'size']):
                col_type = 'integer'
            else:
                # Sample-based detection
                sample = df[col].dropna().head(100).astype(str)
                sample_str = ' '.join(sample)
                if '%' in sample_str:
                    col_type = 'percentage'
                elif any(c in sample_str for c in '$€£¥₹'):
                    col_type = 'money'
                elif pd.api.types.is_numeric_dtype(df[col]):
                    # Check if all are integers
                    if (df[col].dropna() == df[col].dropna().astype(int)).all():
                        col_type = 'integer'
                    else:
                        col_type = 'decimal'
                else:
                    col_type = 'text'
            
            summary['column_types'][col] = col_type
            
            # Convert if not text
            if col_type != 'text':
                converted[col] = df[col].apply(lambda x: ValueParser.parse_single(x, col_type))
                success_rate = converted[col].notna().mean()
                
                if success_rate > 0.5:
                    # Generate examples
                    examples = []
                    for idx in df[col].dropna().head(3).index:
                        original = str(df[col].iloc[idx])
                        parsed = converted[col].iloc[idx]
                        if not pd.isna(parsed):
                            formatted = ValueParser.format_for_display(parsed, col_type)
                            examples.append(f"'{original[:30]}' → {formatted}")
                    
                    summary['converted_columns'].append({
                        'name': col,
                        'type': col_type,
                        'success_rate': f"{int(success_rate * 100)}%",
                        'examples': examples
                    })
                    summary['conversion_examples'][col] = examples
                else:
                    # Conversion failed, revert
                    converted[col] = df[col]
                    summary['skipped_columns'].append(f"{col} (low conversion rate)")
        
        # Special handling for integer columns
        for col in summary['column_types']:
            if summary['column_types'][col] == 'integer' and col in converted:
                converted[col] = pd.to_numeric(converted[col], errors='coerce').astype('Int64')
        
        return converted, summary

class DataFrameProcessor:
    @staticmethod
    def auto_convert(df: pd.DataFrame, api_key: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
        """Fast vectorized conversion"""
        converter = IntelligentDataConverter(api_key)
        return converter.convert_dataframe(df)
    
    @staticmethod
    def generate_sample_data() -> pd.DataFrame:
        """Generate sample data for testing"""
        return pd.DataFrame({
            'Department': ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations'],
            'Employee_Count': [150, 200, 350, 50, 120, 180],
            'Salary_Avg': ['$62k', '$72k', '$95k', '$58k', '$85k', '$67k'],
            'Revenue': ['$2.5M', '$3.8M', '$5.2M', '$1.2M', '$4.5M', '$3.1M'],
            'Profit_Margin': ['25%', '18%', '35%', '12%', '28%', '22%'],
            'Growth_Rate': ['15.5%', '8.2%', '22.1%', '5.3%', '12.7%', '9.8%']
        })