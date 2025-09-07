import os
import io
import tempfile
from typing import Optional

try:
    from google.cloud import speech
    from google.cloud import texttospeech
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    speech = None
    texttospeech = None

class VoiceService:
    """Service for speech-to-text and text-to-speech functionality"""
    
    def __init__(self):
        self.speech_client = None
        self.tts_client = None
        
        if GOOGLE_CLOUD_AVAILABLE and speech and texttospeech:
            try:
                # Initialize Google Cloud clients
                # These will use default credentials or service account key
                self.speech_client = speech.SpeechClient()
                self.tts_client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print(f"Failed to initialize Google Cloud clients: {e}")
                self.speech_client = None
                self.tts_client = None
    
    def speech_to_text(self, audio_data: bytes, language_code: str = "en-US") -> Optional[str]:
        """Convert speech to text using Google Cloud Speech-to-Text"""
        if not self.speech_client:
            return None
        
        try:
            # Map language codes
            language_map = {
                'en': 'en-US',
                'es': 'es-ES',
                'fr': 'fr-FR',
                'de': 'de-DE',
                'zh': 'zh-CN',
                'ja': 'ja-JP'
            }
            
            full_language_code = language_map.get(language_code, language_code)
            if len(language_code) == 2:
                full_language_code = language_map.get(language_code, f"{language_code}-US")
            else:
                full_language_code = language_code
            
            if not speech:
                return None
                
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=full_language_code,
                enable_automatic_punctuation=True,
            )
            
            # Try different audio formats if WEBM fails
            audio_formats = [
                (speech.RecognitionConfig.AudioEncoding.WEBM_OPUS, 48000),
                (speech.RecognitionConfig.AudioEncoding.OGG_OPUS, 48000),
                (speech.RecognitionConfig.AudioEncoding.LINEAR16, 16000),
                (speech.RecognitionConfig.AudioEncoding.FLAC, 44100),
            ]
            
            for encoding, sample_rate in audio_formats:
                try:
                    config = speech.RecognitionConfig(
                        encoding=encoding,
                        sample_rate_hertz=sample_rate,
                        language_code=full_language_code,
                        enable_automatic_punctuation=True,
                    )
                    
                    audio = speech.RecognitionAudio(content=audio_data)
                    response = self.speech_client.recognize(
                        config=config,
                        audio=audio
                    )
                    
                    if response.results:
                        transcript = response.results[0].alternatives[0].transcript
                        return transcript.strip()
                        
                except Exception as format_error:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Speech-to-text error: {e}")
            return None
    
    def text_to_speech(self, text: str, language_code: str = "en-US") -> Optional[bytes]:
        """Convert text to speech using Google Cloud Text-to-Speech"""
        if not self.tts_client or not text:
            return None
        
        try:
            if not texttospeech:
                return None
                
            # Map language codes
            language_map = {
                'en': 'en-US',
                'es': 'es-ES',
                'fr': 'fr-FR',
                'de': 'de-DE',
                'zh': 'zh-CN',
                'ja': 'ja-JP'
            }
            
            full_language_code = language_map.get(language_code, language_code)
            if len(language_code) == 2:
                full_language_code = language_map.get(language_code, f"{language_code}-US")
            else:
                full_language_code = language_code
            
            # Select appropriate voice based on language
            voice_name_map = {
                'en-US': 'en-US-Journey-F',
                'es-ES': 'es-ES-Standard-A',
                'fr-FR': 'fr-FR-Standard-A',
                'de-DE': 'de-DE-Standard-A',
                'zh-CN': 'zh-CN-Standard-A',
                'ja-JP': 'ja-JP-Standard-A'
            }
            
            # Configure synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=full_language_code,
                name=voice_name_map.get(full_language_code),
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0,
                volume_gain_db=0.0
            )
            
            # Synthesize speech
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if voice services are available"""
        return GOOGLE_CLOUD_AVAILABLE and self.speech_client is not None and self.tts_client is not None
