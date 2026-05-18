"""Value parsing utilities with enhanced conversion"""
import re
import numpy as np
import pandas as pd
from typing import Optional, Any

class ValueParser:
    SUFFIX_MAP = {'k': 1e3, 'K': 1e3, 'm': 1e6, 'M': 1e6, 'b': 1e9, 'B': 1e9, 't': 1e12, 'T': 1e12}
    
    @staticmethod
    def parse_value(value: Any, column_type: str) -> Optional[float]:
        """
        Parse a value according to its column type with enhanced detection.
        Handles: $1.2M, 15%, (123), 45.6k, etc.
        """
        if pd.isna(value) or value == '' or value is None:
            return np.nan
        
        str_value = str(value).strip()
        
        # Handle parentheses for negative numbers
        is_negative = False
        if str_value.startswith('(') and str_value.endswith(')'):
            str_value = '-' + str_value[1:-1]
            is_negative = True
        elif str_value.startswith('-'):
            is_negative = True
            str_value = str_value[1:]
        
        # Remove currency symbols and commas
        str_value = re.sub(r'[$€£¥₹]', '', str_value)
        str_value = str_value.replace(',', '')
        str_value = str_value.replace(' ', '')
        
        # Check for percentage sign
        has_percent = '%' in str_value
        str_value = str_value.replace('%', '')
        
        # Parse suffix multipliers (k, M, B, T)
        found_multiplier = 1
        for suffix, multiplier in ValueParser.SUFFIX_MAP.items():
            if str_value.endswith(suffix):
                found_multiplier = multiplier
                str_value = str_value[:-len(suffix)]
                break
        
        # Clean remaining string - keep only digits, decimal point, and minus sign
        str_value = re.sub(r'[^\d\.-]', '', str_value)
        
        if not str_value or str_value == '.' or str_value == '-':
            return np.nan
        
        try:
            base_value = float(str_value) * found_multiplier
            
            # Handle percentage conversion
            if has_percent or column_type == 'percentage':
                # If value > 1, assume it's already in percentage form (e.g., 15% -> 0.15)
                # If value <= 1, assume it's already decimal (e.g., 0.15 -> 0.15)
                if base_value > 1:
                    base_value = base_value / 100
            
            # Apply negative sign
            if is_negative:
                base_value = -base_value
            
            # Apply type-specific rounding
            result = ValueParser._apply_type_formatting(base_value, column_type)
            
            return result
            
        except (ValueError, OverflowError):
            return np.nan
    
    @staticmethod
    def _apply_type_formatting(value: float, column_type: str) -> float:
        """Apply appropriate rounding based on column type"""
        if column_type == 'percentage':
            return round(value, 6)  # More precision for percentages
        elif column_type == 'money':
            return round(value, 2)
        elif column_type == 'integer':
            return round(value)
        elif column_type == 'decimal':
            return round(value, 4)
        else:
            return round(value, 2) if abs(value) >= 1 else round(value, 4)
    
    @staticmethod
    def format_for_display(value: float, column_type: str) -> str:
        """Format a parsed value for human-readable display"""
        if pd.isna(value):
            return 'N/A'
        
        if column_type == 'percentage':
            return f"{value*100:.2f}%"
        elif column_type == 'money':
            if abs(value) >= 1e9:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.2f}M"
            elif abs(value) >= 1e3:
                return f"${value/1e3:.2f}K"
            else:
                return f"${value:,.2f}"
        elif column_type == 'integer':
            return f"{int(value):,}"
        else:
            return f"{value:,.4f}".rstrip('0').rstrip('.')