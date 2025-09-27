#!/usr/bin/env python3
"""
Test script for multilingual features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.language_detection_service import LanguageDetectionService
from services.cultural_context_service import CulturalContextService
from services.multilingual_service import MultilingualService

def test_language_detection():
    """Test language detection service"""
    print("🔍 Testing Language Detection Service...")
    
    detector = LanguageDetectionService()
    
    test_texts = [
        ("Hello, how are you today?", "en"),
        ("Hola, ¿cómo estás hoy?", "es"),
        ("Bonjour, comment allez-vous aujourd'hui?", "fr"),
        ("Guten Tag, wie geht es Ihnen heute?", "de"),
        ("こんにちは、今日はいかがですか？", "ja"),
        ("你好，你今天怎么样？", "zh"),
        ("مرحبا، كيف حالك اليوم؟", "ar"),
        ("नमस्ते, आप आज कैसे हैं?", "hi"),
    ]
    
    for text, expected_lang in test_texts:
        detected_lang, confidence = detector.detect_language(text)
        status = "✅" if detected_lang == expected_lang else "❌"
        print(f"  {status} '{text[:30]}...' -> {detected_lang} ({confidence:.2f}) [expected: {expected_lang}]")
    
    print(f"Language detection available: {detector.is_available()}")

def test_cultural_context():
    """Test cultural context service"""
    print("\n🏛️ Testing Cultural Context Service...")
    
    cultural_service = CulturalContextService()
    
    test_languages = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'ar', 'hi']
    
    for lang in test_languages:
        context = cultural_service.get_cultural_context(lang)
        greeting = cultural_service.get_appropriate_greeting(lang, 'formal')
        tip = cultural_service.get_cultural_tip(lang)
        
        print(f"  🌍 {lang.upper()}: {context.get('region', 'Unknown')}")
        print(f"    Greeting: {greeting}")
        print(f"    Formality: {context.get('formality', 'N/A')}")
        print(f"    Tip: {tip[:50]}...")
        
        # Test cultural sensitivity
        test_text = "I want to discuss politics and money"
        is_safe, warnings = cultural_service.check_cultural_sensitivity(test_text, lang)
        if not is_safe:
            print(f"    ⚠️  Cultural warnings: {', '.join(warnings)}")
        print()

def test_multilingual_service():
    """Test multilingual service capabilities"""
    print("🌐 Testing Multilingual Service...")
    
    multilingual = MultilingualService()
    
    # Test supported languages
    languages = multilingual.get_supported_languages()
    print(f"  📋 Supported languages: {len(languages)}")
    print(f"  🔧 Service available: {multilingual.is_available()}")
    
    # Test basic translation (fallback)
    test_text = "Hello, this is a test message."
    print(f"\n  🔄 Testing translation: '{test_text}'")
    
    for target_lang in ['es', 'fr', 'de']:
        translated = multilingual.translate_text(test_text, target_lang, 'en')
        if translated:
            print(f"    {target_lang}: {translated}")
        else:
            print(f"    {target_lang}: Translation not available")
    
    # Test sentiment analysis
    print(f"\n  😊 Testing sentiment analysis...")
    test_texts = [
        "I love this application! It's amazing!",
        "This is terrible and frustrating.",
        "This is okay, nothing special."
    ]
    
    for text in test_texts:
        sentiment = multilingual.analyze_sentiment(text, 'en')
        print(f"    '{text[:30]}...' -> {sentiment.get('sentiment', 'unknown')} ({sentiment.get('confidence', 0):.2f})")

def main():
    """Run all tests"""
    print("🚀 Testing Multilingual AI Chatbot Features\n")
    print("=" * 60)
    
    try:
        test_language_detection()
        test_cultural_context()
        test_multilingual_service()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()