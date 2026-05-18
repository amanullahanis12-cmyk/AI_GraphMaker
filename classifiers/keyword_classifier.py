"""Keyword-based column classification with enhanced detection"""
import pandas as pd
import re
from typing import Dict

class KeywordClassifier:
    PERCENTAGE_INDICATORS = [
        'percent', 'pct', 'percentage', '%', 'ratio', 'rate', 
        'margin', 'growth', 'share', 'proportion', 'dependency'
    ]
    
    MONEY_INDICATORS = [
        'salary', 'revenue', 'income', 'cost', 'price', 'budget', 
        'expense', 'profit', 'loss', 'asset', 'compensation', 'payment',
        'earning', 'fee', 'net', 'gross', 'total', 'value', 'worth',
        'capital', 'cash', 'fund', 'investment'
    ]
    
    COUNT_INDICATORS = [
        'count', 'number', 'num', 'quantity', 'qty', 'employees', 
        'staff', 'people', 'members', 'items', 'units', 'population', 
        'size', 'headcount'
    ]
    
    def classify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Classify columns based on keywords and sample values"""
        types = {}
        
        for col in df.columns:
            col_lower = col.lower().replace('_', ' ').replace('-', ' ')
            
            # Check for money indicators
            if any(k in col_lower for k in self.MONEY_INDICATORS):
                types[col] = 'money'
            # Check for percentage indicators
            elif any(k in col_lower for k in self.PERCENTAGE_INDICATORS):
                types[col] = 'percentage'
            # Check for count indicators
            elif any(k in col_lower for k in self.COUNT_INDICATORS):
                types[col] = 'integer'
            else:
                # Analyze sample values
                types[col] = self._analyze_values(df[col], col)
        
        return types
    
    def _analyze_values(self, series: pd.Series, col_name: str) -> str:
        """Analyze sample values to determine type"""
        # Check if already numeric
        if pd.api.types.is_numeric_dtype(series):
            values = series.dropna()
            if len(values) == 0:
                return 'text'
            
            # Check if all values are integers
            if (values == values.astype(int)).all():
                return 'integer'
            # Check if values are likely percentages (between 0 and 1)
            elif values.max() <= 1.0 and values.min() >= 0:
                return 'percentage'
            else:
                return 'decimal'
        
        # Check string samples
        sample_values = series.dropna().head(20)
        if len(sample_values) == 0:
            return 'text'
        
        sample_str = ' '.join([str(v) for v in sample_values])
        
        # Check for percentage signs
        if '%' in sample_str:
            return 'percentage'
        
        # Check for currency symbols
        if any(s in sample_str for s in ['$', '€', '£', '¥', '₹']):
            return 'money'
        
        # Check for K/M/B suffixes with money-related keywords
        if any(s in sample_str for s in ['k', 'K', 'M', 'B', 'T']):
            money_keywords = ['salary', 'revenue', 'income', 'cost', 'price', 'budget', 'asset']
            if any(keyword in col_name.lower() for keyword in money_keywords):
                return 'money'
            return 'decimal'
        
        # Try to convert to numeric
        try:
            numeric_values = pd.to_numeric(sample_values, errors='coerce')
            success_rate = numeric_values.notna().sum() / len(sample_values)
            
            if success_rate > 0.8:
                numeric_clean = numeric_values.dropna()
                if len(numeric_clean) > 0:
                    if (numeric_clean == numeric_clean.astype(int)).all():
                        return 'integer'
                    elif numeric_clean.max() <= 1.0 and numeric_clean.min() >= 0:
                        return 'percentage'
                    else:
                        return 'decimal'
        except:
            pass
        
        return 'text'