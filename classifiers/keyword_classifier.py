"""Keyword-based column classification"""
import pandas as pd
from typing import Dict

class KeywordClassifier:
    PERCENTAGE_INDICATORS = ['percent', 'pct', 'percentage', '%', 'ratio', 'rate', 'margin', 'growth']
    MONEY_INDICATORS = ['salary', 'revenue', 'income', 'cost', 'price', 'budget', 'expense', 'profit', 'asset']
    COUNT_INDICATORS = ['count', 'number', 'quantity', 'employees', 'population', 'size']
    
    def classify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        types = {}
        for col in df.columns:
            col_lower = col.lower()
            if any(k in col_lower for k in self.MONEY_INDICATORS):
                types[col] = 'money'
            elif any(k in col_lower for k in self.PERCENTAGE_INDICATORS):
                types[col] = 'percentage'
            elif any(k in col_lower for k in self.COUNT_INDICATORS):
                types[col] = 'integer'
            else:
                types[col] = self._analyze_values(df[col])
        return types
    
    def _analyze_values(self, series: pd.Series) -> str:
        if pd.api.types.is_numeric_dtype(series):
            return 'integer' if (series.dropna() == series.dropna().astype(int)).all() else 'decimal'
        
        sample = ' '.join(series.dropna().head(10).astype(str))
        if '%' in sample:
            return 'percentage'
        if any(s in sample for s in ['$', '€', '£']):
            return 'money'
        return 'text'