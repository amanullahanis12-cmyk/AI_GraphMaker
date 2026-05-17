"""Value parsing utilities"""
import re
import numpy as np
import pandas as pd
from typing import Optional, Any

class ValueParser:
    SUFFIX_MAP = {'k': 1e3, 'K': 1e3, 'm': 1e6, 'M': 1e6, 'b': 1e9, 'B': 1e9}
    
    @staticmethod
    def parse_value(value: Any, column_type: str) -> Optional[float]:
        if pd.isna(value) or value == '':
            return np.nan
        
        str_value = str(value).strip()
        is_negative = str_value.startswith('(') and str_value.endswith(')')
        if is_negative:
            str_value = '-' + str_value[1:-1]
        
        str_value = re.sub(r'[$€£¥₹,]', '', str_value)
        has_percent = '%' in str_value
        str_value = str_value.replace('%', '')
        
        multiplier = 1
        for suffix, mult in ValueParser.SUFFIX_MAP.items():
            if str_value.endswith(suffix):
                multiplier = mult
                str_value = str_value[:-len(suffix)]
                break
        
        str_value = re.sub(r'[^\d\.-]', '', str_value)
        if not str_value or str_value == '.':
            return np.nan
        
        try:
            value = float(str_value) * multiplier
            if has_percent or column_type == 'percentage':
                value = value / 100 if value > 1 else value
            return round(value, 4 if column_type in ['percentage', 'decimal'] else 2)
        except:
            return np.nan