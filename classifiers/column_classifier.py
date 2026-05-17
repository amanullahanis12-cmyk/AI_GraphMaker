"""Main column classifier orchestrator"""
import pandas as pd
from typing import Dict, Optional
from .ai_classifier import AITypeClassifier
from .keyword_classifier import KeywordClassifier

class ColumnClassifier:
    def __init__(self, api_key: Optional[str] = None):
        self.ai_classifier = AITypeClassifier(api_key) if api_key else None
        self.keyword_classifier = KeywordClassifier()
    
    def classify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        if self.ai_classifier:
            try:
                return self.ai_classifier.classify_columns(df)
            except:
                pass
        return self.keyword_classifier.classify_columns(df)