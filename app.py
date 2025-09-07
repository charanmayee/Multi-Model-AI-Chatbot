import streamlit as st
import os
import base64
import io
from PIL import Image
import datetime
import uuid

from services.gemini_service import GeminiService
from services.voice_service import VoiceService
from services.translation_service import TranslationService
from services.content_filter import ContentFilter
from services.export_service import ExportService
from services.chat_sharing import ChatSharing
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
        'voice': VoiceService(),
        'translation': TranslationService(),
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
    if 'voice_enabled' not in st.session_state:
        st.session_state.voice_enabled = False
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "Mixed"

def main():
    st.title("🤖 Multi-Modal AI Chatbot")
    st.markdown("Chat with AI using text, images, and voice. Generate images and get intelligent responses.")
    
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
            ["Mixed", "Text Only", "Image Analysis", "Image Generation", "Voice Chat"],
            index=["Mixed", "Text Only", "Image Analysis", "Image Generation", "Voice Chat"].index(st.session_state.current_mode)
        )
        st.session_state.current_mode = mode
        
        # Language selection
        languages = {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'zh': '中文',
            'ja': '日本語'
        }
        
        selected_language = st.selectbox(
            "Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(st.session_state.language)
        )
        st.session_state.language = selected_language
        
        # Voice settings
        st.session_state.voice_enabled = st.checkbox(
            "Enable Voice Features",
            value=st.session_state.voice_enabled
        )
        
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
                        st.image(message["image"], caption="Generated Image", use_column_width=True)
                    elif isinstance(message["image"], bytes):
                        st.image(message["image"], caption="Uploaded Image", use_column_width=True)
                    else:
                        st.image(message["image"], caption="Image", use_column_width=True)
                
                if message.get("audio") and st.session_state.voice_enabled:
                    st.audio(message["audio"], format="audio/wav")
    
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
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    
    # Voice input (if enabled)
    audio_input = None
    if st.session_state.voice_enabled and mode in ["Mixed", "Voice Chat"]:
        audio_input = st.audio_input("Record your message")
    
    # Text input
    user_input = st.chat_input("Type your message here...")
    
    # Process input
    if user_input or uploaded_image or audio_input:
        process_user_input(
            services,
            user_input,
            uploaded_image,
            audio_input,
            mode,
            selected_language
        )

def process_user_input(services, text_input, image_input, audio_input, mode, language):
    """Process user input and generate AI response"""
    
    # Prepare user message
    user_message = {
        "role": "user",
        "timestamp": datetime.datetime.now().isoformat(),
        "text": text_input or "",
        "image": None,
        "audio": None
    }
    
    # Handle audio input
    if audio_input and st.session_state.voice_enabled:
        try:
            # Convert audio to text
            audio_text = services['voice'].speech_to_text(audio_input.getvalue(), language)
            if audio_text:
                user_message["text"] = audio_text
                user_message["audio"] = audio_input.getvalue()
                st.info(f"Voice input: {audio_text}")
        except Exception as e:
            st.error(f"Voice processing error: {str(e)}")
    
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
                st.image(user_message["image"], caption="Your image", use_column_width=True)
    
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
                
                # Prepare context
                context = {
                    "messages": st.session_state.messages[-10:],  # Last 10 messages for context
                    "mode": mode,
                    "language": language
                }
                
                # Generate response based on mode
                response = generate_ai_response(services, user_message, context)
                
                # Add response to chat
                st.session_state.messages.append(response)
                
                # Display response
                if response.get("text"):
                    st.write(response["text"])
                
                if response.get("image"):
                    st.image(response["image"], caption="Generated Image", use_column_width=True)
                
                if response.get("audio") and st.session_state.voice_enabled:
                    st.audio(response["audio"], format="audio/wav")
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                error_response = {
                    "role": "assistant",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "text": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                    "image": None,
                    "audio": None
                }
                st.session_state.messages.append(error_response)

def generate_ai_response(services, user_message, context):
    """Generate AI response based on user input and context"""
    
    response = {
        "role": "assistant",
        "timestamp": datetime.datetime.now().isoformat(),
        "text": "",
        "image": None,
        "audio": None
    }
    
    mode = context["mode"]
    language = context["language"]
    
    try:
        # Handle different modes
        if mode == "Image Generation" or (mode == "Mixed" and "generate" in user_message["text"].lower() and "image" in user_message["text"].lower()):
            # Generate image
            if user_message["text"]:
                image_data = services['gemini'].generate_image(user_message["text"])
                if image_data:
                    response["image"] = image_data
                    response["text"] = f"I've generated an image based on your prompt: '{user_message['text']}'"
                else:
                    response["text"] = "I couldn't generate an image for that prompt. Please try a different description."
        
        elif mode == "Image Analysis" or (user_message.get("image") and mode in ["Mixed"]):
            # Analyze image
            if user_message.get("image"):
                analysis = services['gemini'].analyze_image(user_message["image"], user_message["text"])
                response["text"] = analysis
            else:
                response["text"] = "Please upload an image for analysis."
        
        else:
            # Text conversation
            conversation_history = [msg for msg in context["messages"] if msg.get("text")]
            response_text = services['gemini'].generate_text_response(
                user_message["text"],
                conversation_history
            )
            response["text"] = response_text
        
        # Translate if needed
        if language != 'en' and response["text"]:
            translated_text = services['translation'].translate_text(
                response["text"],
                target_language=language
            )
            if translated_text:
                response["text"] = translated_text
        
        # Generate voice output if enabled
        if st.session_state.voice_enabled and response["text"]:
            try:
                audio_data = services['voice'].text_to_speech(response["text"], language)
                if audio_data:
                    response["audio"] = audio_data
            except Exception as e:
                st.warning(f"Voice generation failed: {str(e)}")
    
    except Exception as e:
        response["text"] = f"I encountered an error processing your request: {str(e)}"
    
    return response

if __name__ == "__main__":
    main()
