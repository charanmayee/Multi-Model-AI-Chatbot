# Multi-Modal AI Chatbot

## Overview

This is a Streamlit-based multi-modal AI chatbot application that enables users to interact with AI through text and images. The application leverages Google's Gemini AI models for text and vision understanding, providing a comprehensive conversational AI experience with features like content filtering, translation, and chat sharing capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid prototyping and deployment
- **Layout**: Wide layout with expandable sidebar for configuration options
- **Session Management**: Streamlit session state for maintaining conversation history and user preferences
- **File Handling**: Support for image and audio file uploads with validation and size limits

### Backend Architecture
- **Service-Oriented Design**: Modular service architecture with dedicated classes for different functionalities
- **AI Integration**: Google Gemini AI service for text generation and image understanding
- **Content Safety**: Built-in content filtering system with pattern matching for inappropriate content
- **Translation Support**: Google Cloud Translate integration for multi-language capabilities

### Core Services
- **GeminiService**: Handles AI text generation and vision capabilities using Google Gemini models
- **TranslationService**: Provides text translation between multiple languages
- **ContentFilter**: Implements safety measures to block inappropriate content
- **ExportService**: Enables conversation export to various formats (PDF, JSON, TXT)
- **ChatSharing**: Creates shareable links for conversations with expiry management

### Data Management
- **Session Storage**: In-memory storage using Streamlit session state for conversation history
- **File Processing**: PIL-based image processing with support for multiple formats
- **Temporary Storage**: Temporary file handling for audio and image processing
- **Export Formats**: Multiple export options including PDF generation with ReportLab

### Security and Content Safety
- **API Key Management**: Secure handling of API keys through environment variables
- **Content Filtering**: Multi-layered content safety with pattern matching and keyword detection
- **File Validation**: Comprehensive file validation for uploaded content with size and format restrictions
- **Share Link Security**: UUID-based share tokens with configurable expiry times

## External Dependencies

### AI and Machine Learning Services
- **Google Gemini AI**: Primary AI model for text generation and image understanding
- **Google Cloud Translate API**: Multi-language translation services

### Core Python Libraries
- **Streamlit**: Web application framework for the user interface
- **PIL (Pillow)**: Image processing and validation
- **ReportLab**: PDF generation for conversation exports
- **google-genai**: Google Gemini AI client library
- **google-cloud-translate**: Google Cloud Translation services

### Infrastructure Requirements
- **Environment Variables**: GEMINI_API_KEY for AI services, BASE_URL for sharing functionality
- **Google Cloud Credentials**: Service account or default credentials for Google Cloud translation services
- **File System Access**: Temporary file storage for image processing

### Optional Integrations
- **Database Support**: Architecture prepared for database integration for persistent storage
- **Cloud Storage**: Ready for integration with cloud storage services for file management
- **Authentication**: Framework supports future integration of user authentication systems
