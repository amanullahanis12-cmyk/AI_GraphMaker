"""Data conversion orchestrator"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Optional
from classifiers import ColumnClassifier
from .value_parser import ValueParser

class IntelligentDataConverter:
    def __init__(self, api_key: Optional[str] = None):
        self.classifier = ColumnClassifier(api_key)
        self.parser = ValueParser()
    
    def convert_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        converted_df = df.copy()
        column_types = self.classifier.classify_columns(df)
        converted_columns = []
        
        for col, col_type in column_types.items():
            if col_type != 'text':
                converted = df[col].apply(lambda x: self.parser.parse_value(x, col_type))
                if converted.notna().sum() / len(df) > 0.5:
                    converted_df[col] = converted
                    converted_columns.append({'name': col, 'type': col_type})
        
        return converted_df, {'converted_columns': converted_columns, 'column_types': column_types}

class DataFrameProcessor:
    @staticmethod
    def auto_convert(df: pd.DataFrame, api_key: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
        converter = IntelligentDataConverter(api_key)
        return converter.convert_dataframe(df)