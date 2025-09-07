import io
import json
from datetime import datetime
from typing import List, Dict, Any
import base64

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    letter = None
    SimpleDocTemplate = None
    Paragraph = None
    Spacer = None
    getSampleStyleSheet = None
    ParagraphStyle = None
    colors = None

class ExportService:
    """Service for exporting chat conversations to various formats"""
    
    def __init__(self):
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self._setup_styles()
    
    def _setup_styles(self):
        """Setup PDF styles"""
        if not REPORTLAB_AVAILABLE:
            return
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='ChatUser',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.blue,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChatAssistant',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.black,
            spaceAfter=12,
            leftIndent=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='Timestamp',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.grey,
            spaceAfter=3
        ))
    
    def export_to_txt(self, messages: List[Dict[str, Any]]) -> str:
        """Export chat messages to plain text format"""
        output = []
        output.append("Multi-Modal AI Chatbot - Conversation Export")
        output.append("=" * 50)
        output.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        for i, message in enumerate(messages, 1):
            role = "User" if message["role"] == "user" else "Assistant"
            timestamp = message.get("timestamp", "")
            
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%H:%M:%S')
                except:
                    formatted_time = timestamp
                output.append(f"[{formatted_time}] {role}:")
            else:
                output.append(f"{role}:")
            
            # Add text content
            if message.get("text"):
                output.append(message["text"])
            
            # Add image indicators
            if message.get("image"):
                output.append("[Image attached]")
            
            output.append("")  # Empty line between messages
        
        return "\n".join(output)
    
    def export_to_pdf(self, messages: List[Dict[str, Any]], chat_id: str) -> bytes:
        """Export chat messages to PDF format"""
        if not REPORTLAB_AVAILABLE:
            # Fallback to text if reportlab is not available
            text_content = self.export_to_txt(messages)
            return text_content.encode('utf-8')
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        content = []
        
        # Title
        title = Paragraph(
            "Multi-Modal AI Chatbot - Conversation Export",
            self.styles['Title'] if self.styles else None
        )
        content.append(title)
        content.append(Spacer(1, 12))
        
        # Metadata
        metadata = Paragraph(
            f"Chat ID: {chat_id}<br/>Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Total Messages: {len(messages)}",
            self.styles['Normal'] if self.styles else None
        )
        content.append(metadata)
        content.append(Spacer(1, 20))
        
        # Messages
        for message in messages:
            role = "User" if message["role"] == "user" else "Assistant"
            timestamp = message.get("timestamp", "")
            
            # Timestamp
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%H:%M:%S')
                except:
                    formatted_time = timestamp
                
                time_para = Paragraph(
                    f"[{formatted_time}]",
                    self.styles['Timestamp'] if self.styles else None
                )
                content.append(time_para)
            
            # Role and message
            style_name = 'ChatUser' if role == "User" else 'ChatAssistant'
            role_text = f"<b>{role}:</b>"
            
            if message.get("text"):
                message_text = message["text"].replace('\n', '<br/>')
                full_text = f"{role_text} {message_text}"
            else:
                full_text = role_text
            
            message_para = Paragraph(full_text, self.styles[style_name] if self.styles else None)
            content.append(message_para)
            
            # Add indicators for multimedia content
            indicators = []
            if message.get("image"):
                indicators.append("[Image attached]")
            
            if indicators:
                indicator_text = " ".join(indicators)
                indicator_para = Paragraph(
                    f"<i>{indicator_text}</i>",
                    self.styles['Normal'] if self.styles else None
                )
                content.append(indicator_para)
            
            content.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
    
    def export_to_json(self, messages: List[Dict[str, Any]], chat_id: str) -> str:
        """Export chat messages to JSON format"""
        export_data = {
            "chat_id": chat_id,
            "exported_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "messages": []
        }
        
        for message in messages:
            # Create a clean copy without binary data
            clean_message = {
                "role": message["role"],
                "timestamp": message.get("timestamp", ""),
                "text": message.get("text", "")
            }
            
            # Add indicators for multimedia content
            if message.get("image"):
                clean_message["has_image"] = True
            
            export_data["messages"].append(clean_message)
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
