# tutorio/converters/data_converter.py
"""
Main data conversion orchestrator
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, Dict, Optional
from collections import defaultdict

from classifiers import ColumnClassifier
from converters.value_parser import ValueParser


class IntelligentDataConverter:
    """Orchestrates intelligent data type conversion"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.classifier = ColumnClassifier(api_key)
        self.parser = ValueParser()
    
    def convert_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Convert entire DataFrame with intelligent type detection and consistency.
        
        Returns:
            Tuple of (converted_dataframe, conversion_summary)
        """
        converted_df = df.copy()
        summary = self._initialize_summary(df)
        
        # Step 1: Classify all columns
        column_types = self.classifier.classify_columns(df)
        summary['column_types'] = column_types
        summary['classification_method'] = self.classifier.get_classification_method()
        
        # Step 2: Convert each column
        for column in df.columns:
            col_type = column_types.get(column, 'text')
            
            if col_type == 'text':
                summary['skipped_columns'].append(f"{column} (text)")
                continue
            
            # Try conversion
            success, new_values, examples = self._convert_column(df[column], col_type)
            
            if success:
                converted_df[column] = new_values
                summary['converted_columns'].append({
                    'name': column,
                    'type': col_type,
                    'success_rate': f"{new_values.notna().sum()}/{len(df[column])}",
                    'examples': examples[:3]
                })
                summary['conversion_examples'][column] = examples[:3]
            else:
                summary['skipped_columns'].append(f"{column} (low conversion rate)")
        
        # Step 3: Apply consistent rounding (no re‑scaling)
        converted_df = self._apply_consistency_formatting(converted_df, column_types)
        
        return converted_df, summary
    
    def _initialize_summary(self, df: pd.DataFrame) -> Dict:
        """Initialize the conversion summary dictionary"""
        return {
            'total_columns': len(df.columns),
            'converted_columns': [],
            'skipped_columns': [],
            'conversion_examples': {},
            'column_types': {},
            'classification_method': 'keyword'
        }
    
    def _convert_column(self, series: pd.Series, col_type: str) -> Tuple[bool, pd.Series, list]:
        """
        Attempt to convert a single column.
        
        Returns:
            Tuple of (success, converted_series, examples)
        """
        # Test conversion on sample first
        sample = series.dropna().head(20)
        if len(sample) == 0:
            return False, series, []
        
        parsed_sample = sample.apply(lambda x: self.parser.parse_value(x, col_type))
        success_rate = parsed_sample.notna().sum() / len(sample)
        
        if success_rate < 0.5:  # Less than 50% parseable
            return False, series, []
        
        # Convert entire column
        converted = series.apply(lambda x: self.parser.parse_value(x, col_type))
        
        # Generate examples
        examples = []
        for idx in series.dropna().head(5).index:
            original = str(series[idx])
            parsed = converted[idx]
            if not pd.isna(parsed):
                formatted = self.parser.format_for_display(parsed, col_type)
                examples.append(f"'{original}' → {formatted}")
        
        return True, converted, examples
    
    def _apply_consistency_formatting(self, df: pd.DataFrame, column_types: Dict[str, str]) -> pd.DataFrame:
        """
        Apply uniform rounding rules to columns of the same type.
        No additional scaling is performed – the parser already handled value‑to‑decimal conversion.
        """
        result_df = df.copy()
        
        # Group columns by type
        type_groups = defaultdict(list)
        for col, col_type in column_types.items():
            if col in result_df.columns and pd.api.types.is_numeric_dtype(result_df[col]):
                type_groups[col_type].append(col)
        
        # Apply rounding
        for col_type, columns in type_groups.items():
            if col_type == 'percentage':
                for col in columns:
                    result_df[col] = result_df[col].round(4)
            elif col_type == 'money':
                for col in columns:
                    result_df[col] = result_df[col].round(2)
            elif col_type == 'integer':
                for col in columns:
                    result_df[col] = result_df[col].round(0).astype('Int64')
            elif col_type == 'decimal':
                for col in columns:
                    result_df[col] = result_df[col].round(4)
        
        return result_df


class DataFrameProcessor:
    """High-level processor for DataFrame conversion"""
    
    @staticmethod
    def auto_convert(df: pd.DataFrame, api_key: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
        """Automatically convert DataFrame on upload"""
        converter = IntelligentDataConverter(api_key)
        return converter.convert_dataframe(df)
    
    @staticmethod
    def generate_sample_data() -> pd.DataFrame:
        """Generate sample data for testing"""
        return pd.DataFrame({
            'Department': ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations', 'Legal', 'R&D'],
            'Employee_Count': [150, 200, 350, 50, 120, 180, 25, 95],
            'Salary_Avg': ['62k', '72k', '95k', '58k', '85k', '67k', '110k', '88k'],
            'Revenue': ['$2.5M', '$3.8M', '$5.2M', '$1.2M', '$4.5M', '$3.1M', '$1.8M', '$6.2M'],
            'Profit_Margin': ['25%', '18%', '35%', '12%', '28%', '22%', '42%', '31%'],
            'Donor_Dependency': ['100%', '99%', '100%S', '62%', '91%', '75%', '88%', '95%'],
            'Growth_Rate': ['15.5%', '8.2%', '22.1%', '5.3%', '12.7%', '9.8%', '18.4%', '14.6%'],
            'Highest_Compensation': ['$959,665', '$257,551', '$3,622,146', '$1,546,372', '$652,610', '$432,100', '$2,100,000', '$1,234,567'],
            'Net_Assets': ['$578M', '$73M', 'Na', '$10.2B', '$1.1B', '$250M', '$890M', '$4.5B'],
            'surplus_loss': ['$13M', '$19M', 'Na', '$926M', '$198M', '$45M', '$67M', '$234M'],
            'Budget_Allocation': ['$45.5M', '$62.3M', '$120.7M', '$18.2M', '$85.4M', '$55.6M', '$35.8M', '$150.2M']
        })