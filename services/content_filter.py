import re
from typing import Tuple, List

class ContentFilter:
    """Service for content moderation and safety filtering"""
    
    def __init__(self):
        # Define inappropriate content patterns
        self.blocked_patterns = [
            # Violence and harm
            r'\b(kill|murder|violence|harm|hurt|attack)\b',
            # Hate speech indicators
            r'\b(hate|racist|discrimination)\b',
            # Adult content indicators
            r'\b(explicit|adult|nsfw)\b',
            # Dangerous activities
            r'\b(dangerous|illegal|drugs)\b'
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.blocked_patterns]
        
        # Define warning keywords that need extra scrutiny
        self.warning_keywords = [
            'generate', 'create', 'make', 'show', 'display',
            'violence', 'weapon', 'drug', 'illegal', 'harm',
            'naked', 'nude', 'sexual', 'explicit'
        ]
    
    def is_content_safe(self, text: str) -> Tuple[bool, str]:
        """
        Check if content is safe for processing
        Returns: (is_safe: bool, reason: str)
        """
        if not text:
            return True, "Empty content"
        
        text_lower = text.lower().strip()
        
        # Check for blocked patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return False, f"Content contains inappropriate material"
        
        # Check for specific harmful requests
        harmful_requests = [
            "how to make weapons",
            "how to harm",
            "illegal activities",
            "generate explicit",
            "create inappropriate"
        ]
        
        for harmful in harmful_requests:
            if harmful in text_lower:
                return False, f"Request involves harmful content"
        
        # Check for image generation requests that might be problematic
        if any(keyword in text_lower for keyword in ['generate', 'create', 'make']) and 'image' in text_lower:
            if any(warning in text_lower for warning in ['nude', 'naked', 'explicit', 'sexual', 'violence', 'weapon']):
                return False, "Inappropriate image generation request"
        
        return True, "Content approved"
    
    def filter_response(self, text: str) -> str:
        """Filter and clean AI response before displaying"""
        if not text:
            return text
        
        # Remove any potentially harmful instructions
        filtered_text = text
        
        # Replace any remaining inappropriate content with placeholders
        inappropriate_replacements = {
            r'\b(kill|murder)\b': '[inappropriate content removed]',
            r'\b(hate|discrimination)\b': '[inappropriate content removed]',
        }
        
        for pattern, replacement in inappropriate_replacements.items():
            filtered_text = re.sub(pattern, replacement, filtered_text, flags=re.IGNORECASE)
        
        return filtered_text
    
    def moderate_image_prompt(self, prompt: str) -> Tuple[bool, str]:
        """Special moderation for image generation prompts"""
        if not prompt:
            return True, "Empty prompt"
        
        prompt_lower = prompt.lower().strip()
        
        # Specific blocks for image generation
        image_blocks = [
            'nude', 'naked', 'explicit', 'sexual', 'nsfw',
            'violence', 'blood', 'gore', 'weapon', 'gun',
            'illegal', 'drug', 'harm', 'dangerous',
            'hate', 'discrimination', 'offensive'
        ]
        
        for block in image_blocks:
            if block in prompt_lower:
                return False, f"Image prompt contains inappropriate content: {block}"
        
        return True, "Image prompt approved"
    
    def get_content_warning(self, text: str) -> str:
        """Generate appropriate content warning if needed"""
        if not text:
            return ""
        
        text_lower = text.lower()
        warnings = []
        
        if any(word in text_lower for word in ['violence', 'harm', 'dangerous']):
            warnings.append("Content may contain references to violence or harm")
        
        if any(word in text_lower for word in ['medical', 'health', 'diagnosis']):
            warnings.append("Content may contain medical information - consult professionals")
        
        if warnings:
            return "⚠️ " + "; ".join(warnings)
        
        return ""
