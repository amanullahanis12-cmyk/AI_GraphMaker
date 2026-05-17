# tutorio/security/csv_validator.py
"""
CSV file validation and security checks
"""
import re
import io
import csv
import pandas as pd
from typing import Tuple
from .config import SecurityConfig


class CSVValidator:
    """Validates CSV files for security threats"""
    
    @staticmethod
    def validate_csv_content(content: bytes) -> Tuple[bool, str]:
        """Check CSV for injection attacks"""
        try:
            content_str = content.decode('utf-8', errors='ignore')
            
            # Check for CSV injection patterns
            for pattern in SecurityConfig.CSV_INJECTION_PATTERNS:
                if re.search(pattern, content_str, re.MULTILINE):
                    # Check if it's a false positive in data
                    lines = content_str.split('\n')
                    for i, line in enumerate(lines):
                        if re.search(pattern, line):
                            # Allow certain safe patterns in data
                            if pattern in [r'!', r'`', r'\$']:
                                if i > 0:  # Skip header row, these can appear in data
                                    continue
                            return False, f"Potential CSV injection detected: {pattern}"
            
            # Check for malicious formulas
            formula_pattern = r'^[\s]*[=@\+\-].*[\(\)]'
            lines = content_str.split('\n')
            for i, line in enumerate(lines):
                if re.search(formula_pattern, line):
                    # Only flag if it looks like a command
                    if any(cmd in line.lower() for cmd in ['cmd', 'powershell', 'python', 'bash', 'sh', 'exec']):
                        return False, f"Malicious formula detected in row {i+1}"
            
            return True, "CSV validation passed"
            
        except Exception as e:
            return False, f"CSV validation error: {str(e)}"
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate DataFrame for safe operations"""
        
        # Check DataFrame size
        if len(df) > SecurityConfig.MAX_DF_ROWS:
            return False, f"DataFrame exceeds maximum rows: {len(df)} > {SecurityConfig.MAX_DF_ROWS}"
        
        if len(df.columns) > SecurityConfig.MAX_DF_COLUMNS:
            return False, f"DataFrame exceeds maximum columns: {len(df.columns)} > {SecurityConfig.MAX_DF_COLUMNS}"
        
        # Check for suspicious column names
        suspicious_patterns = ['eval', 'exec', '__', 'system', 'cmd', 'shell', 'import', 'os.', 'sys.']
        for col in df.columns:
            col_lower = str(col).lower()
            for pattern in suspicious_patterns:
                if pattern in col_lower:
                    return False, f"Suspicious column name: {col}"
        
        # Validate data types are safe
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check string values for injection attempts
                sample = df[col].dropna().head(100).astype(str)
                for val in sample:
                    if val and len(val) > 0:
                        if val[0] in ['=', '@', '+', '-'] and '(' in val and ')' in val:
                            return False, f"Suspicious value in column {col}: {val[:50]}"
        
        return True, "DataFrame validation passed"