# tutorio/classifiers/keyword_classifier.py
"""
Keyword-based column classification (fallback when AI is unavailable)
"""

import pandas as pd
from typing import Dict


class KeywordClassifier:
    """Rule-based column classification using keyword matching"""
    
    PERCENTAGE_INDICATORS = [
        'percent', 'pct', 'percentage', '%', 'ratio', 'rate',
        'dependency', 'depend', 'portion', 'fraction', 'margin',
        'growth', 'share', 'proportion'
    ]
    
    MONEY_INDICATORS = [
        'salary', 'revenue', 'income', 'compensation', 'cost',
        'price', 'amount', 'budget', 'expense', 'profit', 'loss',
        'asset', 'liability', 'payment', 'earning', 'fee',
        'surplus', 'net', 'gross', 'total', 'value', 'worth',
        'capital', 'cash', 'fund', 'donation', 'grant', 'reimbursement',
        'tuition', 'scholarship', 'loan', 'debt', 'equity', 'payroll',
        'allocation', 'spending', 'investment'
    ]
    
    COUNT_INDICATORS = [
        'count', 'number', 'num', 'quantity', 'qty', 'total_count',
        'employees', 'staff', 'people', 'members', 'items', 'units',
        'population', 'size', 'headcount', 'id'
    ]
    
    def classify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Classify columns based on keywords in column names and sample values.
        """
        column_types = {}
        
        for col in df.columns:
            col_lower = col.lower().replace('_', ' ').replace('-', ' ')
            
            # Check for money indicators
            if self._has_keywords(col_lower, self.MONEY_INDICATORS):
                column_types[col] = 'money'
            
            # Check for percentage indicators
            elif self._has_keywords(col_lower, self.PERCENTAGE_INDICATORS):
                column_types[col] = 'percentage'
            
            # Check for count indicators
            elif self._has_keywords(col_lower, self.COUNT_INDICATORS):
                column_types[col] = 'integer'
            
            # Analyze sample values
            else:
                column_types[col] = self._analyze_values(df[col], col_lower)
        
        return column_types
    
    def _has_keywords(self, text: str, keywords: list) -> bool:
        """Check if text contains any of the keywords"""
        return any(keyword in text for keyword in keywords)
    
    def _analyze_values(self, series: pd.Series, col_name: str) -> str:
        """Analyze sample values to determine type"""
        if pd.api.types.is_numeric_dtype(series):
            # Already numeric - determine specific type
            values = series.dropna()
            if len(values) == 0:
                return 'text'
            
            if (values == values.astype(int)).all():
                return 'integer'
            elif values.max() <= 1.0 and values.min() >= 0:
                return 'percentage'
            else:
                return 'decimal'
        
        # Check string samples
        sample_values = series.dropna().head(10)
        if len(sample_values) == 0:
            return 'text'
        
        sample_str = ' '.join([str(v) for v in sample_values])
        
        if '%' in sample_str:
            return 'percentage'
        elif any(s in sample_str for s in ['$', '€', '£', '¥']):
            return 'money'
        elif any(s in sample_str for s in ['k', 'K', 'M', 'B', 'T']):
            if any(word in col_name for word in ['revenue', 'salary', 'cost', 'asset', 'net']):
                return 'money'
            return 'decimal'
        
        # Try to convert to numeric
        try:
            numeric_values = pd.to_numeric(sample_values, errors='coerce')
            success_rate = numeric_values.notna().sum() / len(sample_values)
            
            if success_rate > 0.8:
                if (numeric_values.dropna() == numeric_values.dropna().astype(int)).all():
                    return 'integer'
                elif numeric_values.max() <= 1.0 and numeric_values.min() >= 0:
                    return 'percentage'
                else:
                    return 'decimal'
        except:
            pass
        
        return 'text'