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
        
        # Language detection and multilingual features
        if 'language_confidence' not in st.session_state:
            st.session_state.language_confidence = 1.0
        
        if 'language_auto_detected' not in st.session_state:
            st.session_state.language_auto_detected = False
        
        if 'detected_languages' not in st.session_state:
            st.session_state.detected_languages = []
        
        if 'cultural_context' not in st.session_state:
            st.session_state.cultural_context = {}
        
        if 'multilingual_enabled' not in st.session_state:
            st.session_state.multilingual_enabled = True
        
        if 'auto_translate' not in st.session_state:
            st.session_state.auto_translate = True
        
        if 'language_switching_animation' not in st.session_state:
            st.session_state.language_switching_animation = True
        
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
        # Support extended language list
        supported_languages = [
            'en', 'es', 'fr', 'de', 'zh', 'ja', 'ar', 'hi', 'pt', 'ru', 'it', 'ko',
            'th', 'vi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'he', 'cs', 'hu',
            'ro', 'bg', 'hr', 'sk', 'sl', 'et', 'lv', 'lt', 'uk', 'be', 'mk', 'sr',
            'bs', 'sq', 'el', 'ca', 'gl', 'eu', 'mt', 'ga', 'cy', 'is', 'fo', 'lb',
            'af', 'am', 'hy', 'az', 'bn', 'my', 'ka', 'gu', 'kn', 'km', 'lo', 'ml',
            'mr', 'ne', 'pa', 'si', 'ta', 'te', 'ur', 'uz', 'id', 'ms', 'tl', 'sw'
        ]
        if language in supported_languages:
            st.session_state.language = language
            # Track language detection confidence if available
            if not hasattr(st.session_state, 'language_confidence'):
                st.session_state.language_confidence = 1.0
            # Track automatic vs manual language selection
            if not hasattr(st.session_state, 'language_auto_detected'):
                st.session_state.language_auto_detected = False
    
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
    
    def set_language_detection_result(self, language: str, confidence: float, auto_detected: bool = True) -> None:
        """Set language detection result"""
        st.session_state.language = language
        st.session_state.language_confidence = confidence
        st.session_state.language_auto_detected = auto_detected
    
    def get_language_detection_info(self) -> Dict[str, Any]:
        """Get language detection information"""
        return {
            'language': st.session_state.language,
            'confidence': getattr(st.session_state, 'language_confidence', 1.0),
            'auto_detected': getattr(st.session_state, 'language_auto_detected', False),
            'detected_languages': getattr(st.session_state, 'detected_languages', [])
        }
    
    def set_cultural_context(self, context: Dict[str, Any]) -> None:
        """Set cultural context for the current language"""
        st.session_state.cultural_context = context
    
    def get_cultural_context(self) -> Dict[str, Any]:
        """Get cultural context"""
        return getattr(st.session_state, 'cultural_context', {})
    
    def set_multilingual_settings(self, enabled: bool, auto_translate: bool = True, animations: bool = True) -> None:
        """Set multilingual feature settings"""
        st.session_state.multilingual_enabled = enabled
        st.session_state.auto_translate = auto_translate
        st.session_state.language_switching_animation = animations
    
    def get_multilingual_settings(self) -> Dict[str, bool]:
        """Get multilingual settings"""
        return {
            'enabled': getattr(st.session_state, 'multilingual_enabled', True),
            'auto_translate': getattr(st.session_state, 'auto_translate', True),
            'animations': getattr(st.session_state, 'language_switching_animation', True)
        }
    
    def add_detected_language(self, language: str, confidence: float) -> None:
        """Add a detected language to the session"""
        if not hasattr(st.session_state, 'detected_languages'):
            st.session_state.detected_languages = []
        
        # Update existing or add new
        for i, (lang, _) in enumerate(st.session_state.detected_languages):
            if lang == language:
                st.session_state.detected_languages[i] = (language, confidence)
                return
        
        st.session_state.detected_languages.append((language, confidence))
        
        # Keep only top 5 detected languages
        st.session_state.detected_languages = sorted(
            st.session_state.detected_languages, 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
