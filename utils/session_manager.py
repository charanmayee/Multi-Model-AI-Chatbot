import streamlit as st
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

class SessionManager:
    """Manages Streamlit session state for the chatbot application"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize all required session state variables"""
        
        # Chat-related state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'chat_id' not in st.session_state:
            st.session_state.chat_id = str(uuid.uuid4())
        
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = []
        
        # User preferences
        if 'language' not in st.session_state:
            st.session_state.language = 'en'
        
        if 'current_mode' not in st.session_state:
            st.session_state.current_mode = "Mixed"
        
        # API and service state
        if 'api_key_configured' not in st.session_state:
            st.session_state.api_key_configured = False
        
        if 'services_initialized' not in st.session_state:
            st.session_state.services_initialized = False
        
        # UI state
        if 'show_settings' not in st.session_state:
            st.session_state.show_settings = False
        
        if 'auto_scroll' not in st.session_state:
            st.session_state.auto_scroll = True
        
        # Export and sharing state
        if 'last_export' not in st.session_state:
            st.session_state.last_export = None
        
        if 'shared_links' not in st.session_state:
            st.session_state.shared_links = []
    
    def add_message(self, role: str, text: str = "", image: Optional[bytes] = None) -> None:
        """Add a message to the conversation"""
        message = {
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "image": image
        }
        
        st.session_state.messages.append(message)
        
        # Update conversation context (keep last 10 messages for context)
        st.session_state.conversation_context = st.session_state.messages[-10:]
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the current conversation"""
        return st.session_state.messages
    
    def get_conversation_context(self) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        return st.session_state.conversation_context
    
    def clear_conversation(self) -> None:
        """Clear the current conversation"""
        st.session_state.messages = []
        st.session_state.conversation_context = []
        st.session_state.chat_id = str(uuid.uuid4())
    
    def set_language(self, language: str) -> None:
        """Set the current language"""
        if language in ['en', 'es', 'fr', 'de', 'zh', 'ja']:
            st.session_state.language = language
    
    def get_language(self) -> str:
        """Get the current language"""
        return st.session_state.language
    
    def set_mode(self, mode: str) -> None:
        """Set the current chat mode"""
        valid_modes = ["Mixed", "Text Only", "Image Analysis", "Image Generation"]
        if mode in valid_modes:
            st.session_state.current_mode = mode
    
    def get_mode(self) -> str:
        """Get the current chat mode"""
        return st.session_state.current_mode
    
    
    def set_api_key_configured(self, configured: bool) -> None:
        """Set API key configuration status"""
        st.session_state.api_key_configured = configured
    
    def is_api_key_configured(self) -> bool:
        """Check if API key is configured"""
        return st.session_state.api_key_configured
    
    def get_chat_stats(self) -> Dict[str, Any]:
        """Get statistics about the current chat"""
        messages = st.session_state.messages
        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        image_count = len([m for m in messages if m.get("image")])
        
        return {
            "chat_id": st.session_state.chat_id,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "images_shared": image_count,
            "language": st.session_state.language,
            "mode": st.session_state.current_mode
        }
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export current session data for backup/sharing"""
        return {
            "chat_id": st.session_state.chat_id,
            "messages": [
                {
                    "role": msg["role"],
                    "timestamp": msg["timestamp"],
                    "text": msg.get("text", ""),
                    "has_image": bool(msg.get("image"))
                }
                for msg in st.session_state.messages
            ],
            "settings": {
                "language": st.session_state.language,
                "mode": st.session_state.current_mode
            },
            "exported_at": datetime.now().isoformat()
        }
    
    def load_session_data(self, session_data: Dict[str, Any]) -> bool:
        """Load session data from backup"""
        try:
            # Clear current session
            self.clear_conversation()
            
            # Load basic info
            st.session_state.chat_id = session_data.get("chat_id", str(uuid.uuid4()))
            
            # Load settings
            settings = session_data.get("settings", {})
            st.session_state.language = settings.get("language", "en")
            st.session_state.current_mode = settings.get("mode", "Mixed")
            
            # Load messages (without binary data)
            messages = session_data.get("messages", [])
            for msg_data in messages:
                message = {
                    "role": msg_data["role"],
                    "timestamp": msg_data["timestamp"],
                    "text": msg_data.get("text", ""),
                    "image": None  # Binary data not preserved
                }
                st.session_state.messages.append(message)
            
            # Update context
            st.session_state.conversation_context = st.session_state.messages[-10:]
            
            return True
            
        except Exception as e:
            print(f"Error loading session data: {e}")
            return False
