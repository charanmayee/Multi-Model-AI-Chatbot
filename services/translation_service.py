import os
from typing import Optional

try:
    from google.cloud import translate_v2 as translate
    TRANSLATE_AVAILABLE = True
except ImportError:
    TRANSLATE_AVAILABLE = False
    translate = None

class TranslationService:
    """Service for text translation using Google Cloud Translate"""
    
    def __init__(self):
        self.client = None
        
        if TRANSLATE_AVAILABLE and translate:
            try:
                self.client = translate.Client()
            except Exception as e:
                print(f"Failed to initialize Google Translate client: {e}")
                self.client = None
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'en') -> Optional[str]:
        """Translate text to target language"""
        if not self.client or not text:
            return None
        
        try:
            # Skip translation if source and target are the same
            if source_language == target_language:
                return text
            
            result = self.client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            
            return result['translatedText']
            
        except Exception as e:
            print(f"Translation error: {e}")
            return None
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of text"""
        if not self.client or not text:
            return None
        
        try:
            result = self.client.detect_language(text)
            return result['language']
            
        except Exception as e:
            print(f"Language detection error: {e}")
            return None
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        if not self.client:
            return []
        
        try:
            languages = self.client.get_languages()
            return [lang['language'] for lang in languages]
            
        except Exception as e:
            print(f"Error getting supported languages: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if translation service is available"""
        return TRANSLATE_AVAILABLE and self.client is not None
