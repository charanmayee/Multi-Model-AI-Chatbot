import os
import logging
from typing import Optional, Tuple, Dict, List
from functools import lru_cache

# Language detection imports with fallbacks
try:
    from langdetect import detect, detect_langs, DetectorFactory
    from langdetect.lang_detect_exception import LangDetectException
    LANGDETECT_AVAILABLE = True
    # Set seed for reproducible results
    DetectorFactory.seed = 0
except ImportError:
    LANGDETECT_AVAILABLE = False
    LangDetectException = Exception

try:
    import fasttext
    FASTTEXT_AVAILABLE = True
except ImportError:
    FASTTEXT_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class LanguageDetectionService:
    """Advanced language detection service with multiple fallbacks"""
    
    def __init__(self):
        self.fasttext_model = None
        self.transformer_pipeline = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize language detection models"""
        # Initialize fastText model if available
        if FASTTEXT_AVAILABLE:
            try:
                # Download model if not exists
                model_path = self._get_fasttext_model()
                if model_path and os.path.exists(model_path):
                    self.fasttext_model = fasttext.load_model(model_path)
                    logger.info("FastText language detection model loaded")
            except Exception as e:
                logger.warning(f"Failed to load FastText model: {e}")
        
        # Initialize transformer pipeline if available
        if TRANSFORMERS_AVAILABLE:
            try:
                self.transformer_pipeline = pipeline(
                    "text-classification",
                    model="papluca/xlm-roberta-base-language-detection"
                )
                logger.info("Transformer language detection pipeline loaded")
            except Exception as e:
                logger.warning(f"Failed to load transformer pipeline: {e}")
    
    def _get_fasttext_model(self) -> Optional[str]:
        """Download and get path to fastText language identification model"""
        try:
            import urllib.request
            model_dir = "/tmp/fasttext_models"
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, "lid.176.bin")
            
            if not os.path.exists(model_path):
                logger.info("Downloading FastText language identification model...")
                urllib.request.urlretrieve(
                    "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin",
                    model_path
                )
                logger.info("FastText model downloaded successfully")
            
            return model_path
        except Exception as e:
            logger.error(f"Failed to download FastText model: {e}")
            return None
    
    @lru_cache(maxsize=1000)
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language of text with confidence score
        Returns: (language_code, confidence)
        """
        if not text or len(text.strip()) < 3:
            return 'en', 0.5  # Default to English for very short text
        
        text = text.strip()
        results = []
        
        # Try langdetect first (most reliable for longer text)
        if LANGDETECT_AVAILABLE:
            try:
                lang_probs = detect_langs(text)
                if lang_probs:
                    best = lang_probs[0]
                    results.append(('langdetect', best.lang, best.prob))
            except LangDetectException:
                pass
        
        # Try fastText as fallback
        if self.fasttext_model:
            try:
                predictions = self.fasttext_model.predict(text.replace('\n', ' '), k=1)
                if predictions[0] and predictions[1]:
                    lang_code = predictions[0][0].replace('__label__', '')
                    confidence = float(predictions[1][0])
                    results.append(('fasttext', lang_code, confidence))
            except Exception as e:
                logger.debug(f"FastText detection failed: {e}")
        
        # Try transformer as final fallback
        if self.transformer_pipeline:
            try:
                pred = self.transformer_pipeline(text[:512])  # Limit text length
                if pred:
                    lang_code = pred[0]['label']
                    confidence = pred[0]['score']
                    results.append(('transformer', lang_code, confidence))
            except Exception as e:
                logger.debug(f"Transformer detection failed: {e}")
        
        # Combine results and return best
        if results:
            # Weight results by method reliability and confidence
            weights = {'langdetect': 1.0, 'fasttext': 0.8, 'transformer': 0.9}
            best_score = 0
            best_lang = 'en'
            
            for method, lang, conf in results:
                weighted_score = conf * weights.get(method, 0.5)
                if weighted_score > best_score:
                    best_score = weighted_score
                    best_lang = lang
            
            return best_lang, min(best_score, 1.0)
        
        return 'en', 0.3  # Default fallback
    
    def detect_language_with_alternatives(self, text: str) -> List[Tuple[str, float]]:
        """
        Detect language with alternative suggestions
        Returns: List of (language_code, confidence) sorted by confidence
        """
        if not text or len(text.strip()) < 3:
            return [('en', 0.5)]
        
        text = text.strip()
        lang_scores = {}
        
        # Collect results from all methods
        if LANGDETECT_AVAILABLE:
            try:
                lang_probs = detect_langs(text)
                for lang_prob in lang_probs[:3]:  # Top 3
                    lang_scores[lang_prob.lang] = max(
                        lang_scores.get(lang_prob.lang, 0),
                        lang_prob.prob
                    )
            except LangDetectException:
                pass
        
        if self.fasttext_model:
            try:
                predictions = self.fasttext_model.predict(text.replace('\n', ' '), k=3)
                for i, lang_code in enumerate(predictions[0]):
                    lang = lang_code.replace('__label__', '')
                    confidence = float(predictions[1][i]) * 0.8  # Slight discount
                    lang_scores[lang] = max(
                        lang_scores.get(lang, 0),
                        confidence
                    )
            except Exception:
                pass
        
        # Sort by confidence and return top results
        sorted_results = sorted(lang_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:5] if sorted_results else [('en', 0.3)]
    
    def is_text_multilingual(self, text: str, threshold: float = 0.7) -> bool:
        """Check if text contains multiple languages"""
        if not text or len(text.strip()) < 20:
            return False
        
        # Split text into sentences and detect language for each
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        if len(sentences) < 2:
            return False
        
        detected_langs = set()
        for sentence in sentences[:5]:  # Check first 5 sentences
            lang, conf = self.detect_language(sentence)
            if conf > threshold:
                detected_langs.add(lang)
        
        return len(detected_langs) > 1
    
    def get_language_info(self, lang_code: str) -> Dict[str, str]:
        """Get detailed language information"""
        # Language code mappings and info
        language_info = {
            'en': {'name': 'English', 'native': 'English', 'family': 'Germanic', 'script': 'Latin'},
            'es': {'name': 'Spanish', 'native': 'Español', 'family': 'Romance', 'script': 'Latin'},
            'fr': {'name': 'French', 'native': 'Français', 'family': 'Romance', 'script': 'Latin'},
            'de': {'name': 'German', 'native': 'Deutsch', 'family': 'Germanic', 'script': 'Latin'},
            'zh': {'name': 'Chinese', 'native': '中文', 'family': 'Sino-Tibetan', 'script': 'Han'},
            'ja': {'name': 'Japanese', 'native': '日本語', 'family': 'Japonic', 'script': 'Hiragana/Katakana/Kanji'},
            'ar': {'name': 'Arabic', 'native': 'العربية', 'family': 'Semitic', 'script': 'Arabic'},
            'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'family': 'Indo-European', 'script': 'Devanagari'},
            'pt': {'name': 'Portuguese', 'native': 'Português', 'family': 'Romance', 'script': 'Latin'},
            'ru': {'name': 'Russian', 'native': 'Русский', 'family': 'Slavic', 'script': 'Cyrillic'},
            'it': {'name': 'Italian', 'native': 'Italiano', 'family': 'Romance', 'script': 'Latin'},
            'ko': {'name': 'Korean', 'native': '한국어', 'family': 'Koreanic', 'script': 'Hangul'},
            'th': {'name': 'Thai', 'native': 'ไทย', 'family': 'Tai-Kadai', 'script': 'Thai'},
            'vi': {'name': 'Vietnamese', 'native': 'Tiếng Việt', 'family': 'Austroasiatic', 'script': 'Latin'},
            'tr': {'name': 'Turkish', 'native': 'Türkçe', 'family': 'Turkic', 'script': 'Latin'},
            'pl': {'name': 'Polish', 'native': 'Polski', 'family': 'Slavic', 'script': 'Latin'},
            'nl': {'name': 'Dutch', 'native': 'Nederlands', 'family': 'Germanic', 'script': 'Latin'},
            'sv': {'name': 'Swedish', 'native': 'Svenska', 'family': 'Germanic', 'script': 'Latin'},
            'da': {'name': 'Danish', 'native': 'Dansk', 'family': 'Germanic', 'script': 'Latin'},
            'no': {'name': 'Norwegian', 'native': 'Norsk', 'family': 'Germanic', 'script': 'Latin'},
            'fi': {'name': 'Finnish', 'native': 'Suomi', 'family': 'Uralic', 'script': 'Latin'},
            'he': {'name': 'Hebrew', 'native': 'עברית', 'family': 'Semitic', 'script': 'Hebrew'},
            'cs': {'name': 'Czech', 'native': 'Čeština', 'family': 'Slavic', 'script': 'Latin'},
            'hu': {'name': 'Hungarian', 'native': 'Magyar', 'family': 'Uralic', 'script': 'Latin'},
            'ro': {'name': 'Romanian', 'native': 'Română', 'family': 'Romance', 'script': 'Latin'},
            'bg': {'name': 'Bulgarian', 'native': 'Български', 'family': 'Slavic', 'script': 'Cyrillic'},
            'hr': {'name': 'Croatian', 'native': 'Hrvatski', 'family': 'Slavic', 'script': 'Latin'},
            'sk': {'name': 'Slovak', 'native': 'Slovenčina', 'family': 'Slavic', 'script': 'Latin'},
            'sl': {'name': 'Slovenian', 'native': 'Slovenščina', 'family': 'Slavic', 'script': 'Latin'},
            'et': {'name': 'Estonian', 'native': 'Eesti', 'family': 'Uralic', 'script': 'Latin'},
            'lv': {'name': 'Latvian', 'native': 'Latviešu', 'family': 'Baltic', 'script': 'Latin'},
            'lt': {'name': 'Lithuanian', 'native': 'Lietuvių', 'family': 'Baltic', 'script': 'Latin'},
            'uk': {'name': 'Ukrainian', 'native': 'Українська', 'family': 'Slavic', 'script': 'Cyrillic'},
            'be': {'name': 'Belarusian', 'native': 'Беларуская', 'family': 'Slavic', 'script': 'Cyrillic'},
            'mk': {'name': 'Macedonian', 'native': 'Македонски', 'family': 'Slavic', 'script': 'Cyrillic'},
            'sr': {'name': 'Serbian', 'native': 'Српски', 'family': 'Slavic', 'script': 'Cyrillic/Latin'},
            'bs': {'name': 'Bosnian', 'native': 'Bosanski', 'family': 'Slavic', 'script': 'Latin'},
            'sq': {'name': 'Albanian', 'native': 'Shqip', 'family': 'Albanian', 'script': 'Latin'},
            'el': {'name': 'Greek', 'native': 'Ελληνικά', 'family': 'Hellenic', 'script': 'Greek'},
            'ca': {'name': 'Catalan', 'native': 'Català', 'family': 'Romance', 'script': 'Latin'},
            'eu': {'name': 'Basque', 'native': 'Euskera', 'family': 'Basque', 'script': 'Latin'},
            'gl': {'name': 'Galician', 'native': 'Galego', 'family': 'Romance', 'script': 'Latin'},
            'is': {'name': 'Icelandic', 'native': 'Íslenska', 'family': 'Germanic', 'script': 'Latin'},
            'mt': {'name': 'Maltese', 'native': 'Malti', 'family': 'Semitic', 'script': 'Latin'},
            'ga': {'name': 'Irish', 'native': 'Gaeilge', 'family': 'Celtic', 'script': 'Latin'},
            'cy': {'name': 'Welsh', 'native': 'Cymraeg', 'family': 'Celtic', 'script': 'Latin'},
            'br': {'name': 'Breton', 'native': 'Brezhoneg', 'family': 'Celtic', 'script': 'Latin'},
            'gd': {'name': 'Scottish Gaelic', 'native': 'Gàidhlig', 'family': 'Celtic', 'script': 'Latin'},
            'kw': {'name': 'Cornish', 'native': 'Kernewek', 'family': 'Celtic', 'script': 'Latin'},
            'fo': {'name': 'Faroese', 'native': 'Føroyskt', 'family': 'Germanic', 'script': 'Latin'},
            'lb': {'name': 'Luxembourgish', 'native': 'Lëtzebuergesch', 'family': 'Germanic', 'script': 'Latin'},
            'rm': {'name': 'Romansh', 'native': 'Rumantsch', 'family': 'Romance', 'script': 'Latin'},
            'oc': {'name': 'Occitan', 'native': 'Occitan', 'family': 'Romance', 'script': 'Latin'},
            'co': {'name': 'Corsican', 'native': 'Corsu', 'family': 'Romance', 'script': 'Latin'},
            'sc': {'name': 'Sardinian', 'native': 'Sardu', 'family': 'Romance', 'script': 'Latin'},
            'fur': {'name': 'Friulian', 'native': 'Furlan', 'family': 'Romance', 'script': 'Latin'},
            'lld': {'name': 'Ladin', 'native': 'Ladin', 'family': 'Romance', 'script': 'Latin'},
        }
        
        return language_info.get(lang_code, {
            'name': lang_code.upper(),
            'native': lang_code.upper(),
            'family': 'Unknown',
            'script': 'Unknown'
        })
    
    def is_available(self) -> bool:
        """Check if at least one detection method is available"""
        return LANGDETECT_AVAILABLE or self.fasttext_model is not None or self.transformer_pipeline is not None