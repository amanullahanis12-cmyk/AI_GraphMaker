"""
Chat history management using Streamlit session state
"""

import streamlit as st
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class ChatHistoryManager:
    """Manages chat history in Streamlit session state"""
    
    @staticmethod
    def initialize():
        """Initialize chat history in session state"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'conversation_id' not in st.session_state:
            st.session_state.conversation_id = str(uuid.uuid4())
        
        if 'current_df' not in st.session_state:
            st.session_state.current_df = None
        
        if 'current_df_name' not in st.session_state:
            st.session_state.current_df_name = None
    
    @staticmethod
    def add_message(role: str, content: str, metadata: Dict = None):
        """Add a message to chat history"""
        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'conversation_id': st.session_state.conversation_id,
            'metadata': metadata or {}
        }
        st.session_state.chat_history.append(message)
    
    @staticmethod
    def get_history() -> List[Dict]:
        """Get all chat messages"""
        return st.session_state.chat_history
    
    @staticmethod
    def clear_history():
        """Clear chat history"""
        st.session_state.chat_history = []
        st.session_state.conversation_id = str(uuid.uuid4())
    
    @staticmethod
    def export_history() -> str:
        """Export chat history as JSON"""
        return json.dumps(st.session_state.chat_history, indent=2)
    
    @staticmethod
    def get_last_n_messages(n: int = 10) -> List[Dict]:
        """Get last N messages for context"""
        return st.session_state.chat_history[-n:]
    
    @staticmethod
    def get_conversation_id() -> str:
        """Get current conversation ID"""
        return st.session_state.conversation_id