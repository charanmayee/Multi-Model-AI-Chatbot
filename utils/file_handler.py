import io
import base64
import tempfile
import os
from typing import Optional, Tuple, Any
from PIL import Image
import mimetypes

class FileHandler:
    """Utility class for handling file operations in the chatbot"""
    
    def __init__(self):
        self.supported_image_formats = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']
        self.supported_audio_formats = ['.wav', '.mp3', '.ogg', '.m4a', '.webm']
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        self.max_audio_size = 25 * 1024 * 1024  # 25MB
    
    def validate_image(self, uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded image file"""
        if not uploaded_file:
            return False, "No file uploaded"
        
        # Check file size
        if uploaded_file.size > self.max_image_size:
            return False, f"Image file too large. Maximum size is {self.max_image_size // (1024*1024)}MB"
        
        # Check file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in self.supported_image_formats:
            return False, f"Unsupported image format. Supported formats: {', '.join(self.supported_image_formats)}"
        
        # Try to open the image to verify it's valid
        try:
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)
            image.verify()
            uploaded_file.seek(0)  # Reset file pointer
            return True, "Valid image"
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    def validate_audio(self, uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded audio file"""
        if not uploaded_file:
            return False, "No file uploaded"
        
        # Check file size
        if uploaded_file.size > self.max_audio_size:
            return False, f"Audio file too large. Maximum size is {self.max_audio_size // (1024*1024)}MB"
        
        # Check file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in self.supported_audio_formats:
            return False, f"Unsupported audio format. Supported formats: {', '.join(self.supported_audio_formats)}"
        
        return True, "Valid audio"
    
    def process_image(self, uploaded_file) -> Optional[Tuple[bytes, dict]]:
        """Process uploaded image and return bytes with metadata"""
        is_valid, message = self.validate_image(uploaded_file)
        if not is_valid:
            raise ValueError(message)
        
        try:
            # Read image
            uploaded_file.seek(0)
            image = Image.open(uploaded_file)
            
            # Get metadata
            metadata = {
                "filename": uploaded_file.name,
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
                "file_size": uploaded_file.size
            }
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            
            # Resize if too large (max 2048x2048 for API efficiency)
            max_dimension = 2048
            if max(image.size) > max_dimension:
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                metadata["resized"] = True
                metadata["new_size"] = image.size
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG', optimize=True)
            img_bytes.seek(0)
            
            return img_bytes.getvalue(), metadata
            
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    def process_audio(self, uploaded_file) -> Optional[Tuple[bytes, dict]]:
        """Process uploaded audio and return bytes with metadata"""
        is_valid, message = self.validate_audio(uploaded_file)
        if not is_valid:
            raise ValueError(message)
        
        try:
            # Read audio data
            uploaded_file.seek(0)
            audio_data = uploaded_file.read()
            
            # Get metadata
            metadata = {
                "filename": uploaded_file.name,
                "file_size": len(audio_data),
                "mime_type": mimetypes.guess_type(uploaded_file.name)[0]
            }
            
            return audio_data, metadata
            
        except Exception as e:
            raise ValueError(f"Error processing audio: {str(e)}")
    
    def image_to_base64(self, image_data: bytes, format: str = "PNG") -> str:
        """Convert image bytes to base64 string for display"""
        try:
            base64_str = base64.b64encode(image_data).decode()
            return f"data:image/{format.lower()};base64,{base64_str}"
        except Exception as e:
            raise ValueError(f"Error converting image to base64: {str(e)}")
    
    def base64_to_image(self, base64_str: str) -> bytes:
        """Convert base64 string back to image bytes"""
        try:
            # Remove the data URL prefix if present
            if base64_str.startswith('data:image/'):
                base64_str = base64_str.split(',', 1)[1]
            
            return base64.b64decode(base64_str)
        except Exception as e:
            raise ValueError(f"Error converting base64 to image: {str(e)}")
    
    def create_temp_file(self, data: bytes, suffix: str = "") -> str:
        """Create a temporary file with the given data"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(data)
                return tmp_file.name
        except Exception as e:
            raise ValueError(f"Error creating temporary file: {str(e)}")
    
    def cleanup_temp_file(self, filepath: str) -> bool:
        """Clean up a temporary file"""
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error cleaning up temp file {filepath}: {e}")
            return False
    
    def get_file_info(self, uploaded_file) -> dict:
        """Get basic information about an uploaded file"""
        if not uploaded_file:
            return {}
        
        return {
            "name": uploaded_file.name,
            "size": uploaded_file.size,
            "type": uploaded_file.type,
            "extension": os.path.splitext(uploaded_file.name)[1].lower()
        }
    
    def is_supported_image(self, filename: str) -> bool:
        """Check if file is a supported image format"""
        extension = os.path.splitext(filename)[1].lower()
        return extension in self.supported_image_formats
    
    def is_supported_audio(self, filename: str) -> bool:
        """Check if file is a supported audio format"""
        extension = os.path.splitext(filename)[1].lower()
        return extension in self.supported_audio_formats
