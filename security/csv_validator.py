"""CSV validation"""
import re
import pandas as pd
from typing import Tuple
from .config import SecurityConfig

class CSVValidator:
    @staticmethod
    def validate_csv_content(content: bytes) -> Tuple[bool, str]:
        try:
            content_str = content.decode('utf-8', errors='ignore')
            for pattern in SecurityConfig.CSV_INJECTION_PATTERNS:
                if re.search(pattern, content_str, re.MULTILINE):
                    return False, f"CSV injection detected"
            return True, "Valid CSV"
        except Exception as e:
            return False, f"Error: {e}"
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
        if len(df) > SecurityConfig.MAX_DF_ROWS:
            return False, "Too many rows"
        suspicious = ['eval', 'exec', '__', 'system', 'cmd']
        for col in df.columns:
            if any(p in str(col).lower() for p in suspicious):
                return False, f"Suspicious column: {col}"
        return True, "Valid"