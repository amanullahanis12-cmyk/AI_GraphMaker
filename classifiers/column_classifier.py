# tutorio/classifiers/column_classifier.py
"""
Main column classifier that orchestrates AI and keyword-based classification
"""

import pandas as pd
from typing import Dict, Optional
from .ai_classifier import AITypeClassifier
from .keyword_classifier import KeywordClassifier


class ColumnClassifier:
    """Orchestrates column classification using AI with keyword fallback"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.ai_classifier = AITypeClassifier(api_key) if api_key else None
        self.keyword_classifier = KeywordClassifier()
    
    def classify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Classify columns using AI first, falling back to keyword analysis.
        Returns dict mapping column_name -> type_category.
        """
        classification_method = 'keyword'
        column_types = {}
        
        # Try AI classification first
        if self.ai_classifier:
            try:
                import streamlit as st
                with st.spinner("🤖 AI analyzing column types..."):
                    column_types = self.ai_classifier.classify_columns(df)
                    # Run consistency check
                    column_types = self.ai_classifier.ensure_consistency(column_types)
                    classification_method = 'ai'
            except Exception as e:
                import streamlit as st
                st.warning(f"AI classification unavailable, using keyword analysis")
        
        # Fallback to keyword classification if AI fails
        if not column_types or classification_method == 'keyword':
            column_types = self.keyword_classifier.classify_columns(df)
        
        # Store classification method for reporting
        self._classification_method = classification_method
        
        return column_types
    
    def get_classification_method(self) -> str:
        """Return the method used for classification ('ai' or 'keyword')"""
        return getattr(self, '_classification_method', 'keyword')