"""Chat history management"""
import streamlit as st
import json
import uuid
from datetime import datetime
from typing import List, Dict

class ChatHistoryManager:
    @staticmethod
    def initialize():
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'conversation_id' not in st.session_state:
            st.session_state.conversation_id = str(uuid.uuid4())
    
    @staticmethod
    def add_message(role: str, content: str, metadata: Dict = None):
        st.session_state.chat_history.append({
            'role': role, 'content': content, 'timestamp': datetime.now().isoformat(),
            'conversation_id': st.session_state.conversation_id, 'metadata': metadata or {}
        })
    
    @staticmethod
    def get_history() -> List[Dict]:
        return st.session_state.chat_history
    
    @staticmethod
    def clear_history():
        st.session_state.chat_history = []
        st.session_state.conversation_id = str(uuid.uuid4())