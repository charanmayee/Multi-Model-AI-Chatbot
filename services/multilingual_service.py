import os
import logging
from typing import Optional, Dict, List, Tuple, Any
from functools import lru_cache
import asyncio

# Import existing translation service
from .translation_service import TranslationService

# M2M100 and transformers imports with fallbacks
try:
    from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class MultilingualService:
    """Enhanced multilingual service with M2M100, BERT multilingual, and advanced features"""
    
    def __init__(self):
        self.google_translate = TranslationService()
        self.m2m100_model = None
        self.m2m100_tokenizer = None
        self.bert_multilingual = None
        self.sentiment_analyzers = {}
        self.language_cache = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize multilingual models"""
        logger.info("Initializing multilingual models...")
        
        # Initialize M2M100 for advanced translation
        if TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE:
            try:
                logger.info("Loading M2M100 model...")
                self.m2m100_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
                self.m2m100_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
                logger.info("M2M100 model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load M2M100 model: {e}")
        
        # Initialize BERT multilingual for understanding
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info("Loading BERT multilingual model...")
                self.bert_multilingual = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("BERT multilingual model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load BERT multilingual model: {e}")
        
        # Initialize sentiment analyzers for multiple languages
        if TRANSFORMERS_AVAILABLE:
            self._initialize_sentiment_analyzers()
    
    def _initialize_sentiment_analyzers(self):
        """Initialize language-specific sentiment analyzers"""
        try:
            # Multilingual sentiment analyzer
            self.sentiment_analyzers['multilingual'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-xlm-roberta-base-sentiment"
            )
            
            # Language-specific analyzers
            sentiment_models = {
                'en': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
                'es': 'pysentimiento/robertuito-sentiment-analysis',
                'fr': 'tblard/tf-allocine',
                'de': 'oliverguhr/german-sentiment-bert',
                'zh': 'uer/roberta-base-finetuned-chinanews-chinese',
                'ja': 'daigo/bert-base-japanese-sentiment',
                'ar': 'CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment',
                'hi': 'l3cube-pune/hindi-bert-v2',
                'pt': 'neuralmind/bert-base-portuguese-cased',
                'ru': 'blanchefort/rubert-base-cased-sentiment'
            }
            
            for lang, model_name in sentiment_models.items():
                try:
                    self.sentiment_analyzers[lang] = pipeline(
                        "sentiment-analysis",
                        model=model_name
                    )
                    logger.info(f"Loaded sentiment analyzer for {lang}")
                except Exception as e:
                    logger.debug(f"Could not load sentiment analyzer for {lang}: {e}")
                    
        except Exception as e:
            logger.warning(f"Failed to initialize sentiment analyzers: {e}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get comprehensive list of supported languages"""
        return {
            'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic',
            'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian',
            'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
            'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh': 'Chinese', 'co': 'Corsican',
            'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch',
            'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino',
            'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician',
            'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati',
            'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew',
            'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic',
            'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian',
            'ja': 'Japanese', 'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh',
            'km': 'Khmer', 'ko': 'Korean', 'ku': 'Kurdish', 'ky': 'Kyrgyz',
            'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian',
            'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay',
            'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori', 'mr': 'Marathi',
            'mn': 'Mongolian', 'my': 'Myanmar', 'ne': 'Nepali', 'no': 'Norwegian',
            'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese',
            'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan',
            'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona',
            'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian',
            'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili',
            'sv': 'Swedish', 'tg': 'Tajik', 'ta': 'Tamil', 'te': 'Telugu',
            'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu',
            'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa',
            'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
        }
    
    def translate_with_m2m100(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate text using M2M100 model"""
        if not self.m2m100_model or not self.m2m100_tokenizer:
            return None
        
        try:
            # Convert language codes to M2M100 format
            m2m100_source = self._convert_to_m2m100_code(source_lang)
            m2m100_target = self._convert_to_m2m100_code(target_lang)
            
            if not m2m100_source or not m2m100_target:
                return None
            
            # Set source language
            self.m2m100_tokenizer.src_lang = m2m100_source
            encoded = self.m2m100_tokenizer(text, return_tensors="pt")
            
            # Generate translation
            generated_tokens = self.m2m100_model.generate(
                **encoded,
                forced_bos_token_id=self.m2m100_tokenizer.get_lang_id(m2m100_target),
                max_length=512,
                num_beams=4,
                early_stopping=True
            )
            
            # Decode translation
            translation = self.m2m100_tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )[0]
            
            return translation
            
        except Exception as e:
            logger.warning(f"M2M100 translation failed: {e}")
            return None
    
    def _convert_to_m2m100_code(self, lang_code: str) -> Optional[str]:
        """Convert standard language code to M2M100 format"""
        m2m100_mapping = {
            'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de', 'zh': 'zh',
            'ja': 'ja', 'ar': 'ar', 'hi': 'hi', 'pt': 'pt', 'ru': 'ru',
            'it': 'it', 'ko': 'ko', 'th': 'th', 'vi': 'vi', 'tr': 'tr',
            'pl': 'pl', 'nl': 'nl', 'sv': 'sv', 'da': 'da', 'no': 'no',
            'fi': 'fi', 'he': 'he', 'cs': 'cs', 'hu': 'hu', 'ro': 'ro',
            'bg': 'bg', 'hr': 'hr', 'sk': 'sk', 'sl': 'sl', 'et': 'et',
            'lv': 'lv', 'lt': 'lt', 'uk': 'uk', 'be': 'be', 'mk': 'mk',
            'sr': 'sr', 'bs': 'bs', 'sq': 'sq', 'el': 'el', 'ca': 'ca',
            'gl': 'gl', 'eu': 'eu', 'mt': 'mt', 'ga': 'ga', 'cy': 'cy',
            'is': 'is', 'fo': 'fo', 'lb': 'lb'
        }
        return m2m100_mapping.get(lang_code)
    
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> Optional[str]:
        """Enhanced translation with multiple methods"""
        if not text or not target_language:
            return None
        
        # Skip if source and target are the same
        if source_language == target_language:
            return text
        
        # Try M2M100 first for better quality
        if source_language and self.m2m100_model:
            m2m100_result = self.translate_with_m2m100(text, source_language, target_language)
            if m2m100_result:
                return m2m100_result
        
        # Fallback to Google Translate
        if self.google_translate.is_available():
            return self.google_translate.translate_text(text, target_language, source_language)
        
        return None
    
    def analyze_sentiment(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """Analyze sentiment with language-specific models"""
        if not text:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'scores': {}}
        
        try:
            # Try language-specific analyzer first
            if language in self.sentiment_analyzers:
                result = self.sentiment_analyzers[language](text)
            elif 'multilingual' in self.sentiment_analyzers:
                result = self.sentiment_analyzers['multilingual'](text)
            else:
                return {'sentiment': 'neutral', 'confidence': 0.0, 'scores': {}}
            
            if result:
                sentiment_result = result[0]
                return {
                    'sentiment': sentiment_result['label'].lower(),
                    'confidence': sentiment_result['score'],
                    'scores': {sentiment_result['label'].lower(): sentiment_result['score']},
                    'language': language
                }
                
        except Exception as e:
            logger.warning(f"Sentiment analysis failed for {language}: {e}")
        
        return {'sentiment': 'neutral', 'confidence': 0.0, 'scores': {}}
    
    def get_text_embeddings(self, text: str) -> Optional[List[float]]:
        """Get multilingual text embeddings using BERT"""
        if not self.bert_multilingual or not text:
            return None
        
        try:
            embeddings = self.bert_multilingual.encode([text])
            return embeddings[0].tolist()
        except Exception as e:
            logger.warning(f"Failed to get text embeddings: {e}")
            return None
    
    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between texts in different languages"""
        if not self.bert_multilingual or not text1 or not text2:
            return 0.0
        
        try:
            embeddings = self.bert_multilingual.encode([text1, text2])
            similarity = self.bert_multilingual.similarity(embeddings[0:1], embeddings[1:2])
            return float(similarity[0][0])
        except Exception as e:
            logger.warning(f"Failed to compute similarity: {e}")
            return 0.0
    
    def detect_code_switching(self, sentences: List[str]) -> Dict[str, Any]:
        """Detect code-switching (multiple languages) in text"""
        if not sentences:
            return {'has_code_switching': False, 'languages': [], 'confidence': 0.0}
        
        from .language_detection_service import LanguageDetectionService
        detector = LanguageDetectionService()
        
        detected_languages = []
        total_confidence = 0.0
        
        for sentence in sentences:
            if len(sentence.strip()) > 5:
                lang, conf = detector.detect_language(sentence)
                detected_languages.append((lang, conf))
                total_confidence += conf
        
        unique_languages = list(set([lang for lang, _ in detected_languages]))
        avg_confidence = total_confidence / len(detected_languages) if detected_languages else 0.0
        
        return {
            'has_code_switching': len(unique_languages) > 1,
            'languages': unique_languages,
            'confidence': avg_confidence,
            'language_distribution': self._calculate_language_distribution(detected_languages)
        }
    
    def _calculate_language_distribution(self, detected_languages: List[Tuple[str, float]]) -> Dict[str, float]:
        """Calculate language distribution in text"""
        if not detected_languages:
            return {}
        
        lang_counts = {}
        total_confidence = 0.0
        
        for lang, conf in detected_languages:
            lang_counts[lang] = lang_counts.get(lang, 0) + conf
            total_confidence += conf
        
        # Normalize to percentages
        if total_confidence > 0:
            return {lang: (count / total_confidence) * 100 
                   for lang, count in lang_counts.items()}
        
        return {}
    
    def get_language_quality_score(self, text: str, language: str) -> float:
        """Assess text quality for a specific language"""
        if not text:
            return 0.0
        
        try:
            # Basic quality indicators
            quality_score = 0.0
            
            # Length factor (reasonable length gets higher score)
            length_score = min(len(text) / 100, 1.0) * 0.3
            quality_score += length_score
            
            # Character diversity (more diverse = higher quality)
            unique_chars = len(set(text.lower()))
            total_chars = len(text)
            if total_chars > 0:
                diversity_score = min(unique_chars / total_chars, 0.5) * 0.3
                quality_score += diversity_score
            
            # Language-specific checks
            if self.bert_multilingual:
                # Use embeddings to assess coherence
                try:
                    sentences = [s.strip() for s in text.split('.') if s.strip()]
                    if len(sentences) > 1:
                        # Check coherence between sentences
                        coherence_scores = []
                        for i in range(len(sentences) - 1):
                            sim = self.compute_semantic_similarity(sentences[i], sentences[i + 1])
                            coherence_scores.append(sim)
                        
                        if coherence_scores:
                            coherence_score = sum(coherence_scores) / len(coherence_scores) * 0.4
                            quality_score += coherence_score
                except Exception:
                    pass
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Failed to assess language quality: {e}")
            return 0.5
    
    @lru_cache(maxsize=100)
    def get_language_features(self, language: str) -> Dict[str, Any]:
        """Get features and characteristics of a language"""
        features = {
            'script': 'Latin',
            'direction': 'ltr',
            'family': 'Unknown',
            'complexity': 'medium',
            'formality_levels': ['informal', 'formal'],
            'has_gender': False,
            'has_cases': False,
            'word_order': 'SVO'
        }
        
        # Language-specific features
        language_features = {
            'zh': {
                'script': 'Han', 'direction': 'ltr', 'family': 'Sino-Tibetan',
                'complexity': 'high', 'formality_levels': ['informal', 'formal', 'honorific'],
                'has_gender': False, 'has_cases': False, 'word_order': 'SVO'
            },
            'ja': {
                'script': 'Hiragana/Katakana/Kanji', 'direction': 'ltr', 'family': 'Japonic',
                'complexity': 'very_high', 'formality_levels': ['casual', 'polite', 'respectful', 'humble'],
                'has_gender': False, 'has_cases': False, 'word_order': 'SOV'
            },
            'ar': {
                'script': 'Arabic', 'direction': 'rtl', 'family': 'Semitic',
                'complexity': 'high', 'formality_levels': ['informal', 'formal', 'classical'],
                'has_gender': True, 'has_cases': True, 'word_order': 'VSO'
            },
            'hi': {
                'script': 'Devanagari', 'direction': 'ltr', 'family': 'Indo-European',
                'complexity': 'medium', 'formality_levels': ['informal', 'formal', 'respectful'],
                'has_gender': True, 'has_cases': True, 'word_order': 'SOV'
            },
            'de': {
                'script': 'Latin', 'direction': 'ltr', 'family': 'Germanic',
                'complexity': 'high', 'formality_levels': ['informal', 'formal'],
                'has_gender': True, 'has_cases': True, 'word_order': 'V2'
            },
            'ru': {
                'script': 'Cyrillic', 'direction': 'ltr', 'family': 'Slavic',
                'complexity': 'high', 'formality_levels': ['informal', 'formal'],
                'has_gender': True, 'has_cases': True, 'word_order': 'SVO'
            },
            'fr': {
                'script': 'Latin', 'direction': 'ltr', 'family': 'Romance',
                'complexity': 'medium', 'formality_levels': ['informal', 'formal'],
                'has_gender': True, 'has_cases': False, 'word_order': 'SVO'
            },
            'es': {
                'script': 'Latin', 'direction': 'ltr', 'family': 'Romance',
                'complexity': 'medium', 'formality_levels': ['informal', 'formal'],
                'has_gender': True, 'has_cases': False, 'word_order': 'SVO'
            },
            'ko': {
                'script': 'Hangul', 'direction': 'ltr', 'family': 'Koreanic',
                'complexity': 'high', 'formality_levels': ['casual', 'polite', 'formal', 'honorific'],
                'has_gender': False, 'has_cases': False, 'word_order': 'SOV'
            }
        }
        
        return language_features.get(language, features)
    
    def is_available(self) -> bool:
        """Check if multilingual service is available"""
        return (self.google_translate.is_available() or 
                self.m2m100_model is not None or 
                len(self.sentiment_analyzers) > 0)