import logging
from typing import Dict, List, Optional, Tuple, Any
from functools import lru_cache
import re

logger = logging.getLogger(__name__)

class CulturalContextService:
    """Service for handling cultural context and appropriate responses"""
    
    def __init__(self):
        self.cultural_data = self._load_cultural_data()
        self.greeting_patterns = self._load_greeting_patterns()
        self.communication_styles = self._load_communication_styles()
        self.cultural_norms = self._load_cultural_norms()
    
    def _load_cultural_data(self) -> Dict[str, Dict[str, Any]]:
        """Load cultural data for different regions/languages"""
        return {
            'en': {
                'region': 'Global English',
                'formality': 'moderate',
                'directness': 'high',
                'hierarchy': 'low',
                'time_orientation': 'monochronic',
                'context': 'low',
                'personal_space': 'high',
                'greetings': ['Hello', 'Hi', 'Good morning', 'Good afternoon', 'Good evening'],
                'farewell': ['Goodbye', 'Bye', 'See you later', 'Have a great day'],
                'politeness_markers': ['please', 'thank you', 'you\'re welcome', 'excuse me'],
                'taboo_topics': ['personal finances', 'age', 'weight'],
                'cultural_values': ['individualism', 'efficiency', 'directness'],
                'business_hours': '9:00-17:00',
                'holidays': ['New Year', 'Christmas', 'Thanksgiving']
            },
            'es': {
                'region': 'Spanish-speaking countries',
                'formality': 'high',
                'directness': 'moderate',
                'hierarchy': 'moderate',
                'time_orientation': 'polychronic',
                'context': 'high',
                'personal_space': 'low',
                'greetings': ['Hola', 'Buenos días', 'Buenas tardes', 'Buenas noches'],
                'farewell': ['Adiós', 'Hasta luego', 'Nos vemos', 'Que tengas buen día'],
                'politeness_markers': ['por favor', 'gracias', 'de nada', 'perdón', 'disculpe'],
                'taboo_topics': ['personal income', 'politics', 'religion'],
                'cultural_values': ['family', 'respect', 'personalismo'],
                'business_hours': '9:00-18:00',
                'holidays': ['Día de los Reyes', 'Semana Santa', 'Día de los Muertos']
            },
            'fr': {
                'region': 'French-speaking countries',
                'formality': 'very_high',
                'directness': 'moderate',
                'hierarchy': 'moderate',
                'time_orientation': 'monochronic',
                'context': 'high',
                'personal_space': 'moderate',
                'greetings': ['Bonjour', 'Bonsoir', 'Salut'],
                'farewell': ['Au revoir', 'À bientôt', 'Bonne journée', 'Bonne soirée'],
                'politeness_markers': ['s\'il vous plaît', 'merci', 'de rien', 'excusez-moi', 'pardon'],
                'taboo_topics': ['money', 'personal life', 'work after hours'],
                'cultural_values': ['intellectualism', 'sophistication', 'formality'],
                'business_hours': '9:00-17:00',
                'holidays': ['Jour de l\'An', 'Pâques', 'Fête du Travail', 'Noël']
            },
            'de': {
                'region': 'German-speaking countries',
                'formality': 'high',
                'directness': 'very_high',
                'hierarchy': 'moderate',
                'time_orientation': 'monochronic',
                'context': 'low',
                'personal_space': 'high',
                'greetings': ['Guten Morgen', 'Guten Tag', 'Guten Abend', 'Hallo'],
                'farewell': ['Auf Wiedersehen', 'Tschüss', 'Schönen Tag noch'],
                'politeness_markers': ['bitte', 'danke', 'entschuldigung', 'verzeihung'],
                'taboo_topics': ['personal finances', 'Nazi era', 'personal questions'],
                'cultural_values': ['punctuality', 'efficiency', 'order', 'directness'],
                'business_hours': '8:00-17:00',
                'holidays': ['Neujahr', 'Ostern', 'Tag der Arbeit', 'Weihnachten']
            },
            'zh': {
                'region': 'Chinese-speaking regions',
                'formality': 'very_high',
                'directness': 'low',
                'hierarchy': 'high',
                'time_orientation': 'long_term',
                'context': 'very_high',
                'personal_space': 'low',
                'greetings': ['你好', '您好', '早上好', '下午好', '晚上好'],
                'farewell': ['再见', '拜拜', '回头见', '慢走'],
                'politeness_markers': ['请', '谢谢', '不客气', '对不起', '抱歉'],
                'taboo_topics': ['politics', 'Taiwan', 'Tibet', 'personal failure'],
                'cultural_values': ['harmony', 'face', 'hierarchy', 'long-term thinking'],
                'business_hours': '9:00-18:00',
                'holidays': ['春节', '清明节', '劳动节', '中秋节', '国庆节']
            },
            'ja': {
                'region': 'Japan',
                'formality': 'very_high',
                'directness': 'very_low',
                'hierarchy': 'very_high',
                'time_orientation': 'long_term',
                'context': 'very_high',
                'personal_space': 'moderate',
                'greetings': ['おはようございます', 'こんにちは', 'こんばんは'],
                'farewell': ['さようなら', 'また明日', 'お疲れ様でした'],
                'politeness_markers': ['お願いします', 'ありがとうございます', 'すみません', '失礼します'],
                'taboo_topics': ['WWII', 'personal failures', 'direct criticism'],
                'cultural_values': ['wa (harmony)', 'respect', 'group consensus', 'face-saving'],
                'business_hours': '9:00-18:00',
                'holidays': ['お正月', 'ゴールデンウィーク', 'お盆', '敬老の日']
            },
            'ar': {
                'region': 'Arabic-speaking countries',
                'formality': 'high',
                'directness': 'moderate',
                'hierarchy': 'high',
                'time_orientation': 'polychronic',
                'context': 'very_high',
                'personal_space': 'low',
                'greetings': ['السلام عليكم', 'أهلا وسهلا', 'مرحبا', 'صباح الخير'],
                'farewell': ['مع السلامة', 'إلى اللقاء', 'الله معك'],
                'politeness_markers': ['من فضلك', 'شكرا', 'عفوا', 'آسف'],
                'taboo_topics': ['alcohol', 'pork', 'personal relationships', 'politics'],
                'cultural_values': ['hospitality', 'honor', 'family', 'religious respect'],
                'business_hours': '8:00-16:00',
                'holidays': ['عيد الفطر', 'عيد الأضحى', 'رمضان', 'رأس السنة الهجرية']
            },
            'hi': {
                'region': 'India (Hindi)',
                'formality': 'high',
                'directness': 'low',
                'hierarchy': 'high',
                'time_orientation': 'polychronic',
                'context': 'high',
                'personal_space': 'low',
                'greetings': ['नमस्ते', 'नमस्कार', 'आदाब', 'सत श्री अकाल'],
                'farewell': ['फिर मिलेंगे', 'अलविदा', 'जाइए'],
                'politeness_markers': ['कृपया', 'धन्यवाद', 'माफ करिए', 'क्षमा करें'],
                'taboo_topics': ['beef', 'caste system', 'partition', 'poverty'],
                'cultural_values': ['respect for elders', 'hospitality', 'spirituality', 'family'],
                'business_hours': '10:00-18:00',
                'holidays': ['दिवाली', 'होली', 'दशहरा', 'ईद', 'गुरु नानक जयंती']
            },
            'pt': {
                'region': 'Portuguese-speaking countries',
                'formality': 'moderate',
                'directness': 'moderate',
                'hierarchy': 'moderate',
                'time_orientation': 'polychronic',
                'context': 'high',
                'personal_space': 'low',
                'greetings': ['Olá', 'Bom dia', 'Boa tarde', 'Boa noite'],
                'farewell': ['Tchau', 'Até logo', 'Até mais', 'Tenha um bom dia'],
                'politeness_markers': ['por favor', 'obrigado/obrigada', 'de nada', 'desculpe'],
                'taboo_topics': ['personal income', 'politics', 'colonial history'],
                'cultural_values': ['warmth', 'personal relationships', 'flexibility'],
                'business_hours': '9:00-18:00',
                'holidays': ['Ano Novo', 'Carnaval', 'Páscoa', 'Natal']
            },
            'ru': {
                'region': 'Russian-speaking countries',
                'formality': 'high',
                'directness': 'high',
                'hierarchy': 'high',
                'time_orientation': 'long_term',
                'context': 'high',
                'personal_space': 'low',
                'greetings': ['Здравствуйте', 'Привет', 'Доброе утро', 'Добрый день'],
                'farewell': ['До свидания', 'Пока', 'Удачи', 'Хорошего дня'],
                'politeness_markers': ['пожалуйста', 'спасибо', 'извините', 'простите'],
                'taboo_topics': ['Soviet era', 'personal finances', 'politics'],
                'cultural_values': ['strength', 'endurance', 'intellectual discourse', 'tradition'],
                'business_hours': '9:00-18:00',
                'holidays': ['Новый год', 'Рождество', 'День Победы', 'Масленица']
            }
        }
    
    def _load_greeting_patterns(self) -> Dict[str, List[str]]:
        """Load greeting patterns for different languages"""
        return {
            'formal': {
                'en': ['Good morning', 'Good afternoon', 'Good evening', 'How do you do?'],
                'es': ['Buenos días', 'Buenas tardes', 'Buenas noches', '¿Cómo está usted?'],
                'fr': ['Bonjour', 'Bonsoir', 'Comment allez-vous?'],
                'de': ['Guten Morgen', 'Guten Tag', 'Guten Abend', 'Wie geht es Ihnen?'],
                'zh': ['您好', '早上好', '下午好', '晚上好'],
                'ja': ['おはようございます', 'こんにちは', 'こんばんは'],
                'ar': ['السلام عليكم', 'صباح الخير', 'مساء الخير'],
                'hi': ['नमस्ते', 'नमस्कार', 'आप कैसे हैं?'],
                'pt': ['Bom dia', 'Boa tarde', 'Boa noite', 'Como está?'],
                'ru': ['Здравствуйте', 'Доброе утро', 'Добрый день', 'Добрый вечер']
            },
            'informal': {
                'en': ['Hi', 'Hello', 'Hey', 'What\'s up?'],
                'es': ['Hola', '¿Qué tal?', '¿Cómo estás?'],
                'fr': ['Salut', 'Coucou', 'Ça va?'],
                'de': ['Hallo', 'Hi', 'Wie geht\'s?'],
                'zh': ['你好', '嗨', '你好吗?'],
                'ja': ['こんにちは', 'やあ', '元気?'],
                'ar': ['مرحبا', 'أهلا', 'كيف الحال?'],
                'hi': ['हैलो', 'क्या हाल है?'],
                'pt': ['Oi', 'Olá', 'Tudo bem?'],
                'ru': ['Привет', 'Здарова', 'Как дела?']
            }
        }
    
    def _load_communication_styles(self) -> Dict[str, Dict[str, str]]:
        """Load communication style preferences by culture"""
        return {
            'high_context': ['zh', 'ja', 'ar', 'hi', 'th', 'vi'],  # Indirect, implicit
            'low_context': ['de', 'en', 'nl', 'sv', 'da', 'no'],   # Direct, explicit
            'formal': ['ja', 'de', 'fr', 'zh', 'ar', 'hi'],        # High formality
            'informal': ['en', 'pt', 'es', 'it', 'nl'],            # More casual
            'hierarchical': ['ja', 'zh', 'ar', 'hi', 'de', 'ru'],  # Respect hierarchy
            'egalitarian': ['en', 'sv', 'da', 'no', 'nl', 'fi']    # Flat structure
        }
    
    def _load_cultural_norms(self) -> Dict[str, Dict[str, Any]]:
        """Load cultural norms and expectations"""
        return {
            'time_sensitivity': {
                'high': ['de', 'en', 'ja', 'sv', 'da', 'no', 'fi'],
                'moderate': ['fr', 'zh', 'ru', 'it'],
                'flexible': ['es', 'pt', 'ar', 'hi', 'th']
            },
            'personal_space': {
                'high': ['en', 'de', 'ja', 'sv', 'da', 'no', 'fi'],
                'moderate': ['fr', 'zh', 'ru', 'it'],
                'low': ['es', 'pt', 'ar', 'hi', 'th']
            },
            'emotional_expression': {
                'reserved': ['ja', 'de', 'sv', 'da', 'no', 'fi'],
                'moderate': ['en', 'fr', 'zh', 'ru'],
                'expressive': ['es', 'pt', 'ar', 'hi', 'it']
            }
        }
    
    @lru_cache(maxsize=500)
    def get_cultural_context(self, language: str) -> Dict[str, Any]:
        """Get cultural context for a language"""
        return self.cultural_data.get(language, self.cultural_data.get('en', {}))
    
    def get_appropriate_greeting(self, language: str, formality: str = 'moderate', time_of_day: str = 'general') -> str:
        """Get culturally appropriate greeting"""
        context = self.get_cultural_context(language)
        
        # Determine formality level
        if context.get('formality') in ['very_high', 'high'] or formality == 'formal':
            greetings = self.greeting_patterns.get('formal', {}).get(language, ['Hello'])
        else:
            greetings = self.greeting_patterns.get('informal', {}).get(language, ['Hi'])
        
        # Select based on time of day if applicable
        if time_of_day == 'morning' and len(greetings) > 0:
            return greetings[0]  # Usually morning greeting
        elif time_of_day == 'afternoon' and len(greetings) > 1:
            return greetings[1] if len(greetings) > 1 else greetings[0]
        elif time_of_day == 'evening' and len(greetings) > 2:
            return greetings[2] if len(greetings) > 2 else greetings[0]
        
        return greetings[0] if greetings else 'Hello'
    
    def adjust_response_style(self, response: str, language: str, user_input: str = '') -> str:
        """Adjust response style based on cultural context"""
        context = self.get_cultural_context(language)
        
        # Apply cultural adjustments
        adjusted_response = response
        
        # Formality adjustments
        if context.get('formality') in ['very_high', 'high']:
            adjusted_response = self._increase_formality(adjusted_response, language)
        
        # Directness adjustments
        if context.get('directness') == 'low':
            adjusted_response = self._reduce_directness(adjusted_response, language)
        elif context.get('directness') == 'very_low':
            adjusted_response = self._add_indirectness(adjusted_response, language)
        
        # Context adjustments
        if context.get('context') in ['high', 'very_high']:
            adjusted_response = self._add_context_markers(adjusted_response, language)
        
        return adjusted_response
    
    def _increase_formality(self, text: str, language: str) -> str:
        """Increase formality of response"""
        context = self.get_cultural_context(language)
        politeness_markers = context.get('politeness_markers', [])
        
        # Add politeness markers if not present
        if politeness_markers and not any(marker in text.lower() for marker in politeness_markers):
            if language == 'ja':
                text = text + ' よろしくお願いします。'
            elif language == 'de':
                text = text + ' Bitte schön.'
            elif language == 'fr':
                text = 'Je vous prie de ' + text.lower()
            elif language == 'zh':
                text = '请问，' + text
        
        return text
    
    def _reduce_directness(self, text: str, language: str) -> str:
        """Reduce directness of response"""
        # Add softening phrases
        softening_phrases = {
            'en': ['I believe', 'It seems', 'Perhaps', 'It might be that'],
            'es': ['Creo que', 'Parece que', 'Quizás', 'Tal vez'],
            'fr': ['Je crois que', 'Il semble que', 'Peut-être', 'Il se peut que'],
            'de': ['Ich glaube', 'Es scheint', 'Vielleicht', 'Möglicherweise'],
            'zh': ['我觉得', '似乎', '也许', '可能'],
            'ja': ['と思います', 'ようです', 'たぶん', 'かもしれません'],
            'ar': ['أعتقد', 'يبدو', 'ربما', 'من المحتمل'],
            'hi': ['मुझे लगता है', 'शायद', 'संभवतः'],
            'pt': ['Eu acho que', 'Parece que', 'Talvez', 'Pode ser que'],
            'ru': ['Я думаю', 'Кажется', 'Возможно', 'Может быть']
        }
        
        phrases = softening_phrases.get(language, softening_phrases['en'])
        if phrases and not any(phrase.lower() in text.lower() for phrase in phrases):
            return f"{phrases[0]} {text.lower()}"
        
        return text
    
    def _add_indirectness(self, text: str, language: str) -> str:
        """Add indirectness for very low directness cultures"""
        if language == 'ja':
            # Add Japanese indirectness patterns
            if not any(marker in text for marker in ['かもしれません', 'と思います', 'ようです']):
                text = text + 'かもしれませんね。'
        elif language == 'zh':
            # Add Chinese indirectness
            if not any(marker in text for marker in ['可能', '也许', '大概']):
                text = '大概' + text
        
        return text
    
    def _add_context_markers(self, text: str, language: str) -> str:
        """Add context markers for high-context cultures"""
        context_markers = {
            'zh': ['众所周知', '如您所知', '正如我们都知道的'],
            'ja': ['ご存知の通り', 'もちろん', 'お察しの通り'],
            'ar': ['كما تعلم', 'بالطبع', 'من المعروف أن'],
            'hi': ['जैसा कि आप जानते हैं', 'जाहिर है', 'स्पष्ट रूप से']
        }
        
        markers = context_markers.get(language, [])
        if markers and len(text) > 50:  # Only for longer responses
            return f"{markers[0]}, {text}"
        
        return text
    
    def check_cultural_sensitivity(self, text: str, language: str) -> Tuple[bool, List[str]]:
        """Check if text is culturally sensitive"""
        context = self.get_cultural_context(language)
        taboo_topics = context.get('taboo_topics', [])
        
        warnings = []
        text_lower = text.lower()
        
        for topic in taboo_topics:
            if topic.lower() in text_lower:
                warnings.append(f"Potentially sensitive topic: {topic}")
        
        # Language-specific checks
        if language == 'zh':
            sensitive_terms = ['taiwan', 'tibet', 'democracy', 'freedom']
            for term in sensitive_terms:
                if term in text_lower:
                    warnings.append(f"Culturally sensitive term for Chinese context: {term}")
        
        elif language == 'ar':
            sensitive_terms = ['alcohol', 'pork', 'dating']
            for term in sensitive_terms:
                if term in text_lower:
                    warnings.append(f"Culturally sensitive term for Arabic context: {term}")
        
        elif language == 'hi':
            sensitive_terms = ['beef', 'caste', 'pakistan']
            for term in sensitive_terms:
                if term in text_lower:
                    warnings.append(f"Culturally sensitive term for Hindi context: {term}")
        
        return len(warnings) == 0, warnings
    
    def get_cultural_tip(self, language: str) -> str:
        """Get a cultural tip for interacting in this language"""
        tips = {
            'zh': "In Chinese culture, saving face is important. Avoid direct criticism and allow graceful ways to agree.",
            'ja': "Japanese communication values harmony (wa). Be indirect and respectful of hierarchy.",
            'ar': "Arabic culture values hospitality and respect. Religious considerations are important.",
            'hi': "Indian culture emphasizes respect for elders and family values. Hierarchy matters.",
            'de': "German culture values directness, punctuality, and efficiency. Be clear and precise.",
            'fr': "French culture appreciates formality and intellectual discourse. Use proper etiquette.",
            'es': "Spanish culture values personal relationships and warm communication. Be friendly and patient.",
            'pt': "Portuguese culture is warm and relationship-focused. Personal connections matter.",
            'ru': "Russian culture values intellectual depth and direct communication. Show respect for knowledge."
        }
        
        return tips.get(language, "Be respectful of cultural differences and local customs.")
    
    def is_available(self) -> bool:
        """Check if cultural context service is available"""
        return len(self.cultural_data) > 0