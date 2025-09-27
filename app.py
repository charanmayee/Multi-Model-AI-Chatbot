import streamlit as st
import os
import base64
import io
from PIL import Image
import datetime
import uuid
import time

from services.gemini_service import GeminiService
from services.translation_service import TranslationService
from services.content_filter import ContentFilter
from services.export_service import ExportService
from services.chat_sharing import ChatSharing
from services.language_detection_service import LanguageDetectionService
from services.multilingual_service import MultilingualService
from services.cultural_context_service import CulturalContextService
from utils.session_manager import SessionManager
from utils.file_handler import FileHandler

# Page configuration
st.set_page_config(
    page_title="Multi-Modal AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def initialize_services():
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    
    return {
        'gemini': GeminiService(gemini_api_key),
        'translation': TranslationService(),
        'multilingual': MultilingualService(),
        'language_detection': LanguageDetectionService(),
        'cultural_context': CulturalContextService(),
        'content_filter': ContentFilter(),
        'export': ExportService(),
        'chat_sharing': ChatSharing()
    }

# Initialize session state
def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chat_id' not in st.session_state:
        st.session_state.chat_id = str(uuid.uuid4())
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "Mixed"

def main():
    st.title("🤖 Multi-Modal AI Chatbot")
    st.markdown("Chat with AI using text and images. Generate images and get intelligent responses.")
    
    # Initialize services and session state
    services = initialize_services()
    initialize_session_state()
    session_manager = SessionManager()
    file_handler = FileHandler()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key input
        api_key = st.text_input(
            "Google AI API Key",
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Enter your Google AI API key for full functionality"
        )
        
        if api_key:
            services['gemini'].update_api_key(api_key)
        
        # Mode selection
        mode = st.selectbox(
            "Chat Mode",
            ["Mixed", "Text Only", "Image Analysis", "Image Generation"],
            index=["Mixed", "Text Only", "Image Analysis", "Image Generation"].index(st.session_state.current_mode) if st.session_state.current_mode in ["Mixed", "Text Only", "Image Analysis", "Image Generation"] else 0
        )
        st.session_state.current_mode = mode
        
        # Enhanced Language selection with auto-detection
        st.subheader("🌍 Language & Cultural Settings")
        
        # Get comprehensive language list
        all_languages = services['multilingual'].get_supported_languages()
        
        # Create language selection columns
        lang_col1, lang_col2 = st.columns([3, 1])
        
        with lang_col1:
            # Main language selector with more languages
            common_languages = {
                'en': 'English', 'es': 'Español', 'fr': 'Français', 'de': 'Deutsch',
                'zh': '中文', 'ja': '日本語', 'ar': 'العربية', 'hi': 'हिन्दी',
                'pt': 'Português', 'ru': 'Русский', 'it': 'Italiano', 'ko': '한국어',
                'th': 'ไทย', 'vi': 'Tiếng Việt', 'tr': 'Türkçe', 'pl': 'Polski',
                'nl': 'Nederlands', 'sv': 'Svenska', 'da': 'Dansk', 'no': 'Norsk',
                'fi': 'Suomi', 'he': 'עברית', 'cs': 'Čeština', 'hu': 'Magyar'
            }
            
            selected_language = st.selectbox(
                "Primary Language",
                options=list(common_languages.keys()),
                format_func=lambda x: common_languages[x],
                index=list(common_languages.keys()).index(st.session_state.language) if st.session_state.language in common_languages else 0,
                help="Select your preferred language for interaction"
            )
        
        with lang_col2:
            # Language detection info
            detection_info = session_manager.get_language_detection_info()
            if detection_info.get('auto_detected', False):
                confidence = detection_info.get('confidence', 0.0)
                st.metric(
                    "Detection Confidence", 
                    f"{confidence:.0%}",
                    help="Confidence level of automatic language detection"
                )
        
        # Auto-detection toggle
        auto_detect = st.checkbox(
            "🔍 Auto-detect language from input",
            value=session_manager.get_multilingual_settings().get('auto_translate', True),
            help="Automatically detect and switch language based on user input"
        )
        
        # Show detected languages if any
        detected_langs = detection_info.get('detected_languages', [])
        if detected_langs and len(detected_langs) > 1:
            st.info(f"🔍 Other detected languages: {', '.join([lang for lang, _ in detected_langs[:3]])}")
        
        # Cultural context indicator
        if selected_language != 'en':
            cultural_context = services['cultural_context'].get_cultural_context(selected_language)
            if cultural_context:
                with st.expander(f"🏛️ Cultural Context - {cultural_context.get('region', 'Unknown')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Formality:** {cultural_context.get('formality', 'N/A').title()}")
                        st.write(f"**Communication:** {cultural_context.get('directness', 'N/A').title()}")
                    with col2:
                        st.write(f"**Context:** {cultural_context.get('context', 'N/A').title()}")
                        st.write(f"**Script:** {cultural_context.get('script', 'N/A')}")
                    
                    # Cultural tip
                    tip = services['cultural_context'].get_cultural_tip(selected_language)
                    if tip:
                        st.info(f"💡 **Cultural Tip:** {tip}")
        
        # Update session state
        if selected_language != st.session_state.language:
            # Language switching animation
            if session_manager.get_multilingual_settings().get('animations', True):
                with st.spinner(f"🔄 Switching to {common_languages.get(selected_language, selected_language)}..."):
                    time.sleep(0.5)  # Brief pause for animation effect
            
            session_manager.set_language_detection_result(selected_language, 1.0, False)
            
            # Set cultural context
            cultural_context = services['cultural_context'].get_cultural_context(selected_language)
            session_manager.set_cultural_context(cultural_context)
            
            st.success(f"✅ Language switched to {common_languages.get(selected_language, selected_language)}")
        
        # Update multilingual settings
        session_manager.set_multilingual_settings(True, auto_detect, True)
        
        st.divider()
        
        # Export options
        st.subheader("📤 Export Chat")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export PDF"):
                if st.session_state.messages:
                    pdf_bytes = services['export'].export_to_pdf(
                        st.session_state.messages,
                        st.session_state.chat_id
                    )
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"chat_{st.session_state.chat_id[:8]}.pdf",
                        mime="application/pdf"
                    )
        
        with col2:
            if st.button("Export TXT"):
                if st.session_state.messages:
                    txt_content = services['export'].export_to_txt(st.session_state.messages)
                    st.download_button(
                        label="Download TXT",
                        data=txt_content,
                        file_name=f"chat_{st.session_state.chat_id[:8]}.txt",
                        mime="text/plain"
                    )
        
        # Share chat
        st.subheader("🔗 Share Chat")
        if st.button("Generate Share Link"):
            if st.session_state.messages:
                share_link = services['chat_sharing'].create_share_link(
                    st.session_state.chat_id,
                    st.session_state.messages
                )
                st.code(share_link, language=None)
                st.success("Share link generated! Valid for 24 hours.")
        
        # Clear chat
        st.divider()
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.session_state.chat_id = str(uuid.uuid4())
            st.rerun()
    
    # Main chat interface
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                if message.get("text"):
                    st.write(message["text"])
                
                if message.get("image"):
                    if isinstance(message["image"], str) and message["image"].startswith("data:image"):
                        st.image(message["image"], caption="Generated Image", use_container_width=True)
                    elif isinstance(message["image"], bytes):
                        st.image(message["image"], caption="Uploaded Image", use_container_width=True)
                    else:
                        st.image(message["image"], caption="Image", use_container_width=True)
                
    
    # Input section
    st.divider()
    
    # Image upload (if applicable)
    uploaded_image = None
    if mode in ["Mixed", "Image Analysis"]:
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
            key=f"image_upload_{len(st.session_state.messages)}"
        )
        
        if uploaded_file:
            uploaded_image = Image.open(uploaded_file)
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    
    
    # Text input
    user_input = st.chat_input("Type your message here...")
    
    # Process input
    if user_input or uploaded_image:
        process_user_input(
            services,
            user_input,
            uploaded_image,
            mode,
            selected_language
        )

def process_user_input(services, text_input, image_input, mode, language):
    """Process user input and generate AI response with enhanced multilingual support"""
    
    # Get session manager for multilingual features
    session_manager = SessionManager()
    multilingual_settings = session_manager.get_multilingual_settings()
    
    # Language detection and switching
    detected_language = language
    detection_confidence = 1.0
    
    if text_input and multilingual_settings.get('auto_translate', True):
        # Detect language of user input
        detected_language, detection_confidence = services['language_detection'].detect_language(text_input)
        
        # Update session if confidence is high enough and language is different
        if detection_confidence > 0.7 and detected_language != language:
            session_manager.set_language_detection_result(detected_language, detection_confidence, True)
            session_manager.add_detected_language(detected_language, detection_confidence)
            
            # Show language detection info
            st.info(f"🔍 Detected language: {detected_language.upper()} (confidence: {detection_confidence:.0%})")
            language = detected_language
    
    # Prepare user message with multilingual metadata
    user_message = {
        "role": "user",
        "timestamp": datetime.datetime.now().isoformat(),
        "text": text_input or "",
        "image": None,
        "detected_language": detected_language,
        "detection_confidence": detection_confidence,
        "original_language": language
    }
    
    # Handle image input
    if image_input:
        # Convert PIL Image to bytes
        img_bytes = io.BytesIO()
        image_input.save(img_bytes, format='PNG')
        user_message["image"] = img_bytes.getvalue()
    
    # Add user message to chat
    if user_message["text"] or user_message["image"]:
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            if user_message["text"]:
                st.write(user_message["text"])
            if user_message["image"]:
                st.image(user_message["image"], caption="Your image", use_container_width=True)
    
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Content filtering
                if user_message["text"]:
                    is_safe, filter_reason = services['content_filter'].is_content_safe(user_message["text"])
                    if not is_safe:
                        st.error(f"Content blocked: {filter_reason}")
                        return
                    
                    # Cultural sensitivity check
                    is_culturally_appropriate, cultural_warnings = services['cultural_context'].check_cultural_sensitivity(
                        user_message["text"], language
                    )
                    if not is_culturally_appropriate and cultural_warnings:
                        st.warning(f"⚠️ Cultural sensitivity note: {'; '.join(cultural_warnings)}")
                
                # Get cultural context for response styling
                cultural_context = services['cultural_context'].get_cultural_context(language)
                
                # Prepare enhanced context
                context = {
                    "messages": st.session_state.messages[-10:],  # Last 10 messages for context
                    "mode": mode,
                    "language": language,
                    "cultural_context": cultural_context,
                    "multilingual_enabled": multilingual_settings.get('enabled', True),
                    "detected_language": detected_language,
                    "detection_confidence": detection_confidence
                }
                
                # Generate response based on mode
                response = generate_ai_response(services, user_message, context)
                
                # Add response to chat
                st.session_state.messages.append(response)
                
                # Display response
                if response.get("text"):
                    st.write(response["text"])
                
                if response.get("image"):
                    st.image(response["image"], caption="Generated Image", use_container_width=True)
                
                # Show additional multilingual info if enabled
                if multilingual_settings.get('enabled', True) and response.get("text"):
                    # Sentiment analysis
                    sentiment_result = services['multilingual'].analyze_sentiment(response["text"], language)
                    if sentiment_result.get('confidence', 0) > 0.8:
                        sentiment_emoji = {"positive": "😊", "negative": "😔", "neutral": "😐"}.get(
                            sentiment_result.get('sentiment', 'neutral'), "😐"
                        )
                        st.caption(f"{sentiment_emoji} Sentiment: {sentiment_result.get('sentiment', 'neutral').title()} "
                                 f"({sentiment_result.get('confidence', 0):.0%})")
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                error_response = {
                    "role": "assistant",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "text": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                    "image": None
                }
                st.session_state.messages.append(error_response)

def generate_ai_response(services, user_message, context):
    """Generate AI response with enhanced multilingual and cultural context support"""
    
    response = {
        "role": "assistant",
        "timestamp": datetime.datetime.now().isoformat(),
        "text": "",
        "image": None,
        "language": context["language"],
        "cultural_context_applied": False
    }
    
    mode = context["mode"]
    language = context["language"]
    cultural_context = context.get("cultural_context", {})
    multilingual_enabled = context.get("multilingual_enabled", True)
    
    try:
        # Handle different modes
        if mode == "Image Generation" or (mode == "Mixed" and "generate" in user_message["text"].lower() and "image" in user_message["text"].lower()):
            # Generate image
            if user_message["text"]:
                image_data = services['gemini'].generate_image(user_message["text"])
                if image_data:
                    response["image"] = image_data
                    # Get culturally appropriate response text
                    if cultural_context.get('formality') in ['very_high', 'high']:
                        response["text"] = f"I have respectfully created an image based on your request: '{user_message['text']}'"
                    else:
                        response["text"] = f"I've generated an image based on your prompt: '{user_message['text']}'"
                else:
                    response["text"] = "I couldn't generate an image for that prompt. Please try a different description."
        
        elif mode == "Image Analysis" or (user_message.get("image") and mode in ["Mixed"]):
            # Analyze image
            if user_message.get("image"):
                analysis = services['gemini'].analyze_image(user_message["image"], user_message["text"])
                response["text"] = analysis
            else:
                # Culturally appropriate request for image
                if cultural_context.get('formality') in ['very_high', 'high']:
                    response["text"] = "I would be pleased to analyze an image if you could kindly provide one."
                else:
                    response["text"] = "Please upload an image for analysis."
        
        else:
            # Text conversation with cultural context
            conversation_history = [msg for msg in context["messages"] if msg.get("text")]
            
            # Add cultural context to prompt if available
            cultural_prompt_addition = ""
            if cultural_context:
                formality = cultural_context.get('formality', 'moderate')
                directness = cultural_context.get('directness', 'moderate')
                
                if formality in ['very_high', 'high']:
                    cultural_prompt_addition += " Please respond in a formal and respectful manner."
                if directness == 'low':
                    cultural_prompt_addition += " Please be indirect and diplomatic in your response."
                elif directness == 'very_low':
                    cultural_prompt_addition += " Please use very indirect communication with softening language."
            
            # Generate base response
            enhanced_prompt = user_message["text"] + cultural_prompt_addition
            response_text = services['gemini'].generate_text_response(
                enhanced_prompt,
                conversation_history
            )
            response["text"] = response_text
        
        # Apply cultural adjustments to response
        if multilingual_enabled and cultural_context and response["text"]:
            adjusted_response = services['cultural_context'].adjust_response_style(
                response["text"], 
                language, 
                user_message.get("text", "")
            )
            if adjusted_response != response["text"]:
                response["text"] = adjusted_response
                response["cultural_context_applied"] = True
        
        # Enhanced translation with M2M100 if available
        if language != 'en' and response["text"]:
            # Try M2M100 first for better quality
            translated_text = services['multilingual'].translate_text(
                response["text"],
                target_language=language,
                source_language='en'
            )
            
            # Fallback to Google Translate if needed
            if not translated_text and services['translation'].is_available():
                translated_text = services['translation'].translate_text(
                    response["text"],
                    target_language=language
                )
            
            if translated_text:
                response["text"] = translated_text
        
        # Add greeting if this is the first message and culturally appropriate
        if len(context.get("messages", [])) <= 1 and not user_message.get("image"):
            greeting = services['cultural_context'].get_appropriate_greeting(language, 'moderate')
            if greeting and greeting.lower() not in response["text"].lower()[:50]:
                response["text"] = f"{greeting}! {response['text']}"
    
    except Exception as e:
        # Generate culturally appropriate error message
        if cultural_context.get('formality') in ['very_high', 'high']:
            response["text"] = f"I sincerely apologize, but I encountered a technical difficulty: {str(e)}. Please allow me to try again."
        else:
            response["text"] = f"I encountered an error processing your request: {str(e)}"
    
    return response
    
    return response

if __name__ == "__main__":
    main()
