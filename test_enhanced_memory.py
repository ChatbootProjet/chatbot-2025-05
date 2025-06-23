#!/usr/bin/env python3
"""
Enhanced Memory System Test
اختبار نظام الذاكرة المحسن
"""

import json
import os
from app import (
    init_user_profile_memory, 
    get_user_long_term_memory, 
    save_user_long_term_memory,
    detect_conversation_topics,
    get_enhanced_conversation_context,
    record_enhanced_message
)

print("Enhanced Memory System Test")
print("Testing user profiles and context awareness...")

def test_user_memory():
    """Test user long-term memory functionality"""
    print("🧠 Testing Enhanced Memory System...")
    
    # Test user profile creation
    user_id = "test_user_123"
    
    # Get initial profile
    profile = get_user_long_term_memory(user_id)
    print(f"📊 Initial profile: {profile}")
    
    # Update profile with preferences
    profile["frequently_discussed_topics"] = ["programming", "technology"]
    profile["language_preference"] = "arabic"
    profile["conversation_style"] = "detailed"
    profile["relevant_context"] = ["We discussed Python programming", "User prefers detailed explanations"]
    
    # Save profile
    save_user_long_term_memory(user_id, profile)
    print(f"💾 Saved profile for user: {user_id}")
    
    # Test retrieval
    retrieved_profile = get_user_long_term_memory(user_id)
    print(f"📤 Retrieved profile: {retrieved_profile}")
    
    return retrieved_profile

def test_topic_detection():
    """Test conversation topic detection"""
    print("\n🔍 Testing Topic Detection...")
    
    test_messages = [
        {"message": "I want to learn Python programming", "role": "user"},
        {"message": "Can you help me with machine learning algorithms?", "role": "user"},
        {"message": "How do I design a website?", "role": "user"},
        {"message": "أريد تعلم البرمجة بلغة جافا سكريبت", "role": "user"}
    ]
    
    topics = detect_conversation_topics(test_messages)
    print(f"🏷️ Detected topics: {topics}")
    
    return topics

def test_enhanced_conversation():
    """Test enhanced conversation recording"""
    print("\n💬 Testing Enhanced Conversation Recording...")
    
    session_id = "test_session_456"
    
    # Record some messages with different content types
    record_enhanced_message(session_id, "user", "Hello, I want to learn about AI", None)
    record_enhanced_message(session_id, "assistant", "I'd be happy to help you learn about AI!")
    
    # Record message with file
    file_data = {
        "filename": "test_image.jpg",
        "file_type": "images",
        "file_url": "/uploads/images/test_image.jpg"
    }
    record_enhanced_message(session_id, "user", "Analyze this image", file_data)
    
    print(f"✅ Recorded enhanced messages for session: {session_id}")

def test_enhanced_context():
    """Test enhanced context retrieval"""
    print("\n🎯 Testing Enhanced Context Retrieval...")
    
    session_id = "test_session_456"
    context = get_enhanced_conversation_context(session_id, limit=10)
    
    print(f"📋 Enhanced context (length: {len(context)}):")
    for i, msg in enumerate(context):
        print(f"  {i+1}. {msg['role']}: {msg['parts'][0][:50]}...")
    
    return context

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 ENHANCED MEMORY SYSTEM TEST | اختبار نظام الذاكرة المحسن")
    print("=" * 60)
    
    try:
        # Test user memory
        profile = test_user_memory()
        
        # Test topic detection
        topics = test_topic_detection()
        
        # Test enhanced conversation
        test_enhanced_conversation()
        
        # Test enhanced context
        context = test_enhanced_context()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ تمت جميع الاختبارات بنجاح!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print(f"❌ فشل الاختبار: {e}")
        return False

if __name__ == "__main__":
    main() 