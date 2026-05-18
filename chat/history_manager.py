"""Simple chat history"""
import streamlit as st
import uuid
from datetime import datetime

class ChatHistoryManager:
    @staticmethod
    def initialize():
        st.session_state.setdefault('chat_history', [])
        st.session_state.setdefault('conv_id', str(uuid.uuid4()))
    
    @staticmethod
    def add_message(role: str, content: str, metadata: dict = None):
        st.session_state.chat_history.append({
            'role': role, 'content': content, 'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        })
    
    @staticmethod
    def get_history():
        return st.session_state.get('chat_history', [])
    
    @staticmethod
    def clear_history():
        st.session_state.chat_history = []