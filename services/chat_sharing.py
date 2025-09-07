import json
import base64
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

class ChatSharing:
    """Service for sharing chat conversations via unique links"""
    
    def __init__(self):
        # In a production environment, this would use a proper database
        # For now, we'll use a simple in-memory storage
        self.shared_chats = {}
        self.base_url = os.getenv("BASE_URL", "http://localhost:5000")
    
    def create_share_link(self, chat_id: str, messages: List[Dict[str, Any]], expiry_hours: int = 24) -> str:
        """Create a shareable link for a chat conversation"""
        # Generate a unique share token
        share_token = str(uuid.uuid4())
        
        # Calculate expiry time
        expiry_time = datetime.now() + timedelta(hours=expiry_hours)
        
        # Prepare shareable data (remove binary content)
        shareable_messages = []
        for message in messages:
            clean_message = {
                "role": message["role"],
                "timestamp": message.get("timestamp", ""),
                "text": message.get("text", "")
            }
            
            # Add indicators for multimedia content
            if message.get("image"):
                clean_message["has_image"] = True
            
            shareable_messages.append(clean_message)
        
        # Store the shared chat data
        self.shared_chats[share_token] = {
            "chat_id": chat_id,
            "messages": shareable_messages,
            "created_at": datetime.now().isoformat(),
            "expires_at": expiry_time.isoformat(),
            "view_count": 0
        }
        
        # Generate the share link
        share_link = f"{self.base_url}/shared/{share_token}"
        return share_link
    
    def get_shared_chat(self, share_token: str) -> Optional[Dict[str, Any]]:
        """Retrieve a shared chat by its token"""
        if share_token not in self.shared_chats:
            return None
        
        shared_data = self.shared_chats[share_token]
        
        # Check if the link has expired
        expiry_time = datetime.fromisoformat(shared_data["expires_at"])
        if datetime.now() > expiry_time:
            # Clean up expired link
            del self.shared_chats[share_token]
            return None
        
        # Increment view count
        shared_data["view_count"] += 1
        
        return shared_data
    
    def delete_shared_chat(self, share_token: str) -> bool:
        """Delete a shared chat link"""
        if share_token in self.shared_chats:
            del self.shared_chats[share_token]
            return True
        return False
    
    def cleanup_expired_chats(self):
        """Remove expired shared chats"""
        current_time = datetime.now()
        expired_tokens = []
        
        for token, data in self.shared_chats.items():
            expiry_time = datetime.fromisoformat(data["expires_at"])
            if current_time > expiry_time:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.shared_chats[token]
        
        return len(expired_tokens)
    
    def get_share_stats(self, share_token: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a shared chat"""
        if share_token not in self.shared_chats:
            return None
        
        shared_data = self.shared_chats[share_token]
        
        return {
            "chat_id": shared_data["chat_id"],
            "created_at": shared_data["created_at"],
            "expires_at": shared_data["expires_at"],
            "view_count": shared_data["view_count"],
            "message_count": len(shared_data["messages"])
        }
    
    def export_shared_chat(self, share_token: str, format_type: str = "json") -> Optional[str]:
        """Export a shared chat in the specified format"""
        shared_data = self.get_shared_chat(share_token)
        if not shared_data:
            return None
        
        if format_type == "json":
            export_data = {
                "chat_id": shared_data["chat_id"],
                "shared_at": shared_data["created_at"],
                "messages": shared_data["messages"]
            }
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        elif format_type == "txt":
            output = []
            output.append("Shared Chat Conversation")
            output.append("=" * 30)
            output.append(f"Chat ID: {shared_data['chat_id']}")
            output.append(f"Shared at: {shared_data['created_at']}")
            output.append("")
            
            for message in shared_data["messages"]:
                role = "User" if message["role"] == "user" else "Assistant"
                output.append(f"{role}: {message.get('text', '')}")
                
                if message.get("has_image"):
                    output.append("  [Image was attached]")
                
                output.append("")
            
            return "\n".join(output)
        
        return None
