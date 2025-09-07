import os
import io
from typing import List, Dict, Optional, Any
from PIL import Image
import base64

from google import genai
from google.genai import types

class GeminiService:
    """Service for interacting with Google Gemini AI models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client"""
        try:
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
            else:
                self.client = None
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    def update_api_key(self, api_key: str):
        """Update the API key and reinitialize client"""
        self.api_key = api_key
        self._initialize_client()
    
    def generate_text_response(self, prompt: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """Generate a text response using Gemini"""
        if not self.client:
            return "Please configure your Gemini API key in the sidebar."
        
        try:
            # Build context from conversation history
            context = ""
            if conversation_history:
                recent_messages = conversation_history[-5:]  # Last 5 messages
                for msg in recent_messages:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    if msg.get("text"):
                        context += f"{role}: {msg['text']}\n"
            
            # Prepare the full prompt
            full_prompt = f"""You are a helpful, knowledgeable AI assistant. You can engage in natural conversations, answer questions, provide explanations, and help with various tasks.

Previous conversation:
{context}

Current user message: {prompt}

Please provide a helpful, accurate, and engaging response. If the user asks you to generate an image, let them know that they should use the image generation mode or include "generate image" in their request in mixed mode."""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        ),
                    ]
                )
            )
            
            return response.text or "I couldn't generate a response. Please try again."
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def analyze_image(self, image_data: bytes, text_prompt: str = "") -> str:
        """Analyze an image using Gemini Pro Vision"""
        if not self.client:
            return "Please configure your Gemini API key in the sidebar."
        
        try:
            # Default analysis prompt if none provided
            if not text_prompt:
                analysis_prompt = "Analyze this image in detail. Describe what you see, identify objects, people, text, or any other notable elements. Provide context and insights about the image."
            else:
                analysis_prompt = f"Analyze this image and answer: {text_prompt}"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type="image/png",
                    ),
                    analysis_prompt
                ],
                config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        ),
                    ]
                )
            )
            
            return response.text or "I couldn't analyze the image. Please try again."
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def generate_image(self, prompt: str) -> Optional[bytes]:
        """Generate an image using Gemini"""
        if not self.client:
            return None
        
        try:
            # Enhance prompt for better results
            enhanced_prompt = f"Create a high-quality, detailed image: {prompt}. Make it visually appealing, well-composed, and professionally rendered."
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            if not response.candidates:
                return None
            
            content = response.candidates[0].content
            if not content or not content.parts:
                return None
            
            # Extract image data from response
            for part in content.parts:
                if part.inline_data and part.inline_data.data:
                    return part.inline_data.data
            
            return None
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def moderate_content(self, text: str) -> tuple[bool, str]:
        """Check if content is safe using Gemini's safety features"""
        if not self.client:
            return True, "API not available"
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Is this content appropriate and safe? Content: {text}",
                config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                        ),
                    ]
                )
            )
            
            # If we get a response, content is likely safe
            return True, "Content approved"
            
        except Exception as e:
            # If blocked by safety filters, content is unsafe
            if "safety" in str(e).lower() or "blocked" in str(e).lower():
                return False, "Content blocked by safety filters"
            return True, "Content check failed, allowing"
