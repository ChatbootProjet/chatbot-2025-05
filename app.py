from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
import random
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import time
import config
import json
import os
import uuid
import mimetypes
import traceback
from werkzeug.utils import secure_filename

# Try to import Gemini API
try:
    import google.generativeai as genai
    genai_available = True
    print("✅ Gemini API available")
except ImportError:
    genai_available = False
    print("❌ Gemini API not available")
from werkzeug.utils import secure_filename
from collections import defaultdict
import google.generativeai as genai
import traceback
import markdown2
import bleach
from functools import wraps
import firebase_admin
from firebase_admin import credentials, db
import threading

app = Flask(__name__)
app.secret_key = 'chatbot_learning_secret_key'  # Secret key for session management
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'files': {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'zip'}
}

# Create upload directories if they don't exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'files'), exist_ok=True)

# Function to check if file extension is allowed
def allowed_file(filename, file_type='files'):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'].get(file_type, set())

# Function to get file type based on extension
def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in app.config['ALLOWED_EXTENSIONS']['images']:
        return 'images'
    return 'files'

# Download NLTK data on first run
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Initialize Gemini API
try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(
        model_name=config.GEMINI_MODEL,
        generation_config={
            "temperature": config.GEMINI_TEMPERATURE,
            "max_output_tokens": config.GEMINI_MAX_OUTPUT_TOKENS,
            "top_p": config.GEMINI_TOP_P,
            "top_k": config.GEMINI_TOP_K
        }
    )
    gemini_available = True
    print("Gemini API initialized successfully")
except Exception as e:
    print(f"Error initializing Gemini API: {e}")
    gemini_available = False
    traceback.print_exc()

# Initialize Firebase Admin SDK
firebase_initialized = False

# Check if we should use Firebase (can be disabled for development)
USE_FIREBASE = os.getenv('USE_FIREBASE', 'true').lower() == 'true'

if USE_FIREBASE and config.USE_FIREBASE_STORAGE:
    try:
        if not firebase_admin._apps:
            # Try to use service account file if available
            service_account_path = config.FIREBASE_SERVICE_ACCOUNT or 'firebase-service-account.json'
            
            if os.path.exists(service_account_path):
                # Check if the service account file has real credentials
                with open(service_account_path, 'r') as f:
                    service_data = json.load(f)
                    if 'temp_private_key_for_development' in service_data.get('private_key', ''):
                        print("⚠️  Using temporary service account - Firebase disabled")
                        print("📝 To enable Firebase:")
                        print("   1. Go to Firebase Console > Project Settings > Service Accounts")
                        print("   2. Generate new private key")
                        print("   3. Replace firebase-service-account.json with the downloaded file")
                        raise Exception("Temporary service account detected")
                
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': config.FIREBASE_CONFIG["databaseURL"]
                })
                firebase_initialized = True
                print("✅ Firebase Admin SDK initialized successfully")
            else:
                print("❌ Service account file not found")
                print("📝 To enable Firebase:")
                print("   1. Download service account key from Firebase Console")
                print("   2. Save as 'firebase-service-account.json'")
                raise Exception("Service account file not found")
                
    except Exception as e:
        print(f"⚠️  Firebase initialization failed: {e}")
        print("🔄 Running in LOCAL MODE - conversations stored locally only")
        firebase_initialized = False
else:
    print("🔄 Firebase disabled - running in LOCAL MODE")
    firebase_initialized = False

# Memory Management - Enhanced System
# Enhanced conversation memory with semantic context preservation
CONVERSATION_MEMORY_FILE = 'data/conversation_memory.json'
LEARNING_MEMORY_FILE = 'data/learning_memory.json'
USER_PROFILE_MEMORY_FILE = 'data/user_profiles.json'  # New: Long-term user memory

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Initialize enhanced conversation memory with context preservation
def init_conversation_memory():
    if os.path.exists(CONVERSATION_MEMORY_FILE):
        with open(CONVERSATION_MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

# Initialize enhanced learning memory with semantic understanding
def init_learning_memory():
    if os.path.exists(LEARNING_MEMORY_FILE):
        with open(LEARNING_MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "pattern_frequency": {},
            "user_corrections": {},
            "similar_queries": defaultdict(list),
            "contextual_patterns": {},  # New: Context-aware patterns
            "topic_transitions": {},    # New: Track how topics change
            "user_preferences": {},     # New: User behavior patterns
            "semantic_clusters": {}     # New: Group similar conversations
        }

# Initialize user profile memory for long-term personalization
def init_user_profile_memory():
    if os.path.exists(USER_PROFILE_MEMORY_FILE):
        with open(USER_PROFILE_MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

# Enhanced conversation context with semantic understanding
def get_enhanced_conversation_context(session_id, limit=None):
    """
    Get conversation context with semantic understanding and relevance scoring
    الحصول على سياق المحادثة مع فهم دلالي وتقييم الصلة
    """
    if not limit:
        limit = config.CONTEXT_MESSAGES
    
    user_id = get_user_id_from_session()
    context = []
    
    # Get current conversation context
    current_conversation = []
    if session_id in conversation_memory and len(conversation_memory[session_id]) > 0:
        current_conversation = conversation_memory[session_id][-limit:]
    
    # Get user's long-term memory patterns
    user_profile = get_user_long_term_memory(user_id)
    
    # Add current conversation with enhanced context
    for msg in current_conversation:
        role = "user" if msg["role"] == "user" else "assistant"
        content = msg["message"]
        
        # Add metadata for better context understanding
        enhanced_msg = {"role": role, "parts": [content]}
        
        # Add file context if present
        if "file_data" in msg:
            file_info = msg["file_data"]
            if file_info.get("file_type") == "images":
                enhanced_msg["parts"].append(f"[Image: {file_info.get('filename', 'image')}]")
            else:
                enhanced_msg["parts"].append(f"[File: {file_info.get('filename', 'document')}]")
        
        context.append(enhanced_msg)
    
    # Add relevant context from user's history if available
    if user_profile.get("relevant_context"):
        for relevant_msg in user_profile["relevant_context"][-3:]:  # Last 3 relevant contexts
            context.insert(0, {
                "role": "assistant", 
                "parts": [f"[Previous context: {relevant_msg}]"]
            })
    
    return context

# Enhanced user long-term memory
def get_user_long_term_memory(user_id):
    """
    Get user's long-term memory profile for personalization
    الحصول على ملف الذاكرة طويلة الأمد للمستخدم للتخصيص
    """
    user_profiles = init_user_profile_memory()
    
    if user_id == 'anonymous':
        return {}
    
    return user_profiles.get(user_id, {
        "preferences": {},
        "frequently_discussed_topics": [],
        "conversation_style": "balanced",
        "language_preference": "auto",
        "relevant_context": [],
        "personal_info": {},
        "learning_patterns": {}
    })

# Save enhanced user memory
def save_user_long_term_memory(user_id, profile_data):
    """
    Save user's long-term memory profile
    حفظ ملف الذاكرة طويلة الأمد للمستخدم
    """
    if user_id == 'anonymous':
        return
    
    user_profiles = init_user_profile_memory()
    user_profiles[user_id] = profile_data
    
    with open(USER_PROFILE_MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_profiles, f, ensure_ascii=False, indent=2)

# Enhanced topic detection and memory
def detect_conversation_topics(messages):
    """
    Detect main topics in conversation for better context management
    اكتشاف المواضيع الرئيسية في المحادثة لإدارة أفضل للسياق
    """
    topics = []
    
    # Common topic keywords
    topic_keywords = {
        "programming": ["code", "كود", "برمجة", "script", "function", "دالة", "python", "javascript"],
        "education": ["learn", "تعلم", "study", "درس", "school", "مدرسة", "university", "جامعة"],
        "technology": ["computer", "كمبيوتر", "software", "برمجيات", "AI", "ذكي", "technology", "تقنية"],
        "personal": ["myself", "نفسي", "family", "عائلة", "work", "عمل", "job", "وظيفة"],
        "creative": ["design", "تصميم", "art", "فن", "music", "موسيقى", "write", "كتابة"],
        "science": ["science", "علم", "research", "بحث", "experiment", "تجربة", "theory", "نظرية"]
    }
    
    all_text = " ".join([msg.get("message", "") for msg in messages])
    all_text_lower = all_text.lower()
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in all_text_lower for keyword in keywords):
            topics.append(topic)
    
    return topics

# Enhanced message recording with semantic analysis
def record_enhanced_message(session_id, role, message, file_data=None):
    """
    Enhanced message recording with semantic analysis and context preservation
    تسجيل محسن للرسائل مع تحليل دلالي وحفظ السياق
    """
    user_id = get_user_id_from_session()
    
    message_data = {
        "role": role,
        "message": message,
        "timestamp": time.time(),
        "session_id": session_id
    }
    
    # Add file data if present
    if file_data:
        message_data["file_data"] = file_data
    
    # Analyze message for semantic understanding
    if role == "user":
        # Detect topics and update user profile
        user_profile = get_user_long_term_memory(user_id)
        
        # Update frequently discussed topics
        current_topics = detect_conversation_topics([message_data])
        for topic in current_topics:
            if topic not in user_profile.get("frequently_discussed_topics", []):
                user_profile.setdefault("frequently_discussed_topics", []).append(topic)
        
        # Keep only last 10 topics to avoid clutter
        if len(user_profile.get("frequently_discussed_topics", [])) > 10:
            user_profile["frequently_discussed_topics"] = user_profile["frequently_discussed_topics"][-10:]
        
        # Detect language preference
        detected_lang = detect_language(message)
        if detected_lang:
            user_profile["language_preference"] = detected_lang
        
        # Save updated profile
        save_user_long_term_memory(user_id, user_profile)
    
    # === FIREBASE FIRST APPROACH ===
    if firebase_initialized and user_id != 'anonymous':
        # Load existing conversation from Firebase
        firebase_conversation = get_conversations_from_firebase(user_id).get(session_id, [])
        
        # Add new message
        firebase_conversation.append(message_data)
        
        # Enhanced: Keep more history for better context (100 messages instead of 50)
        if len(firebase_conversation) > 100:
            # Keep first 20 messages (important early context) and last 80 messages
            firebase_conversation = firebase_conversation[:20] + firebase_conversation[-80:]
        
        # Save back to Firebase
        success = save_conversation_to_firebase(user_id, session_id, firebase_conversation)
        if success:
            print(f"🔥 Enhanced message saved to Firebase for user {user_id}")
            
            # Update local memory for current session (cache)
            conversation_memory[session_id] = firebase_conversation
            return
    
    # === FALLBACK TO LOCAL STORAGE ===
    # For anonymous users or when Firebase is not available
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    
    conversation_memory[session_id].append(message_data)
    
    # Enhanced: Keep more messages locally too (60 instead of 30)
    if len(conversation_memory[session_id]) > 60:
        conversation_memory[session_id] = conversation_memory[session_id][-60:]
    
    # Save to user-specific local storage as backup
    if user_id != 'anonymous':
        save_user_conversation_locally(user_id, session_id, conversation_memory[session_id])
        print(f"💾 Enhanced message saved locally for user {user_id}")
    else:
        # Save to global memory for anonymous users
        save_conversation_memory(conversation_memory)
        print(f"💾 Anonymous enhanced message saved locally")

# Enhanced context-aware response generation
def get_context_aware_response(user_input, session_id, file_data=None):
    """
    Enhanced context-aware response generation with semantic understanding
    توليد استجابة واعية بالسياق مع فهم دلالي محسن
    """
    language = detect_language(user_input)
    
    # Get enhanced conversation context
    context = get_enhanced_conversation_context(session_id)
    
    # Get user's long-term memory profile
    user_id = get_user_id_from_session()
    user_profile = get_user_long_term_memory(user_id)
    
    # Build context-aware prompt
    prompt = build_context_aware_prompt(user_input, context, user_profile, language)
    
    try:
        # Use Gemini for enhanced response
        response = gemini_model.generate_content(prompt)
        
        if response and response.text:
            # Truncate extremely long responses to prevent browser crashes
            if len(response.text) > config.MAX_RESPONSE_LENGTH:
                response_text = response.text[:config.MAX_RESPONSE_LENGTH] + "\n\n[Response truncated to prevent browser issues]"
                if language == "arabic":
                    response_text = response.text[:config.MAX_RESPONSE_LENGTH] + "\n\n[تم اقتطاع الاستجابة لتجنب مشاكل المتصفح]"
            else:
                response_text = response.text
            
            # Record the enhanced interaction
            record_enhanced_message(session_id, "user", user_input, file_data)
            record_enhanced_message(session_id, "assistant", response_text)
            
            # Update user's long-term memory
            topics = detect_conversation_topics([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response_text}
            ])
            
            if topics:
                user_profile["recent_topics"] = topics
                user_profile["last_interaction"] = time.time()
                save_user_long_term_memory(user_id, user_profile)
            
            return response_text
            
    except Exception as e:
        print(f"Error in context-aware response: {e}")
        traceback.print_exc()
        
        # Fallback to basic response
        return get_response(user_input, session_id)

def build_context_aware_prompt(user_input, context, user_profile, language):
    """
    Build a comprehensive prompt with enhanced context and user profile
    بناء prompt شامل مع سياق محسن وملف المستخدم
    """
    
    # Ensure user_profile is a dictionary, default to empty dict if None
    if user_profile is None:
        user_profile = {}
    
    # Get user's name or identifier
    user_name = user_profile.get("name", "المستخدم")
    user_topics = user_profile.get("favorite_topics", [])
    user_communication_style = user_profile.get("communication_style", "friendly")
    
    # Ensure context is a list and limit its size
    if context is None:
        context = []
    elif not isinstance(context, list):
        context = []
    
    # Build the enhanced prompt based on language
    if language == "arabic":
        system_prompt = f"""أنت مساعد ذكي يدعى "المساعد الذكي" وتتحدث مع {user_name}.

معلومات عن المستخدم:
- اهتماماته المفضلة: {', '.join(user_topics) if user_topics else 'غير محدد'}
- أسلوب التواصل المفضل: {user_communication_style}

تعليمات مهمة جداً:
- لا تستخدم markdown أو تنسيق HTML أبداً
- اكتب الكود كنص عادي بدون أي رموز تنسيق
- لا تستخدم ``` أو ** أو * أو _ أو أي رموز تنسيق
- اجعل النص بسيط وعادي تماماً
- عند كتابة كود، ضعه في سطور منفصلة بدون تنسيق
- قدم إجابات واضحة ومباشرة
- تجنب الرموز التي قد تسبب مشاكل في المتصفح

المحادثة السابقة:
{context[-3:] if len(context) > 0 else 'لا توجد محادثة سابقة'}

السؤال الحالي: {user_input}

يرجى الإجابة بشكل مفيد ومفصل باللغة العربية، مع مراعاة سياق المحادثة والتفضيلات المذكورة."""

    else:
        system_prompt = f"""You are an intelligent assistant called "Smart Assistant" talking to {user_name}.

User Information:
- Favorite topics: {', '.join(user_topics) if user_topics else 'Not specified'}
- Preferred communication style: {user_communication_style}

VERY IMPORTANT INSTRUCTIONS:
- Do not use markdown or HTML formatting EVER
- Write code as plain text without any formatting symbols
- Do not use ``` or ** or * or _ or any formatting symbols
- Keep text simple and plain
- When writing code, put it on separate lines without formatting
- Provide clear and direct answers
- Avoid symbols that might cause browser issues

Previous conversation:
{context[-3:] if len(context) > 0 else 'No previous conversation'}

Current question: {user_input}

Please provide a helpful and detailed response in English, considering the conversation context and mentioned preferences."""

    return system_prompt

# Save conversation memory
def save_conversation_memory(memory):
    with open(CONVERSATION_MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# Save user-specific conversation to local file
def save_user_conversation_locally(user_id, conversation_id, conversation_data):
    """Save conversation data locally organized by user"""
    if user_id == 'anonymous':
        return  # Don't save anonymous conversations permanently
    
    user_data_dir = f'data/users/{user_id}'
    os.makedirs(user_data_dir, exist_ok=True)
    
    user_conversations_file = f'{user_data_dir}/conversations.json'
    
    # Load existing conversations for this user
    if os.path.exists(user_conversations_file):
        with open(user_conversations_file, 'r', encoding='utf-8') as f:
            user_conversations = json.load(f)
    else:
        user_conversations = {}
    
    # Update with new conversation data
    user_conversations[conversation_id] = conversation_data
    
    # Save back to file
    with open(user_conversations_file, 'w', encoding='utf-8') as f:
        json.dump(user_conversations, f, ensure_ascii=False, indent=2)

# Load user-specific conversations from local file
def load_user_conversations_locally(user_id):
    """Load conversation data for a specific user from local storage"""
    if user_id == 'anonymous':
        return {}
    
    user_conversations_file = f'data/users/{user_id}/conversations.json'
    
    if os.path.exists(user_conversations_file):
        with open(user_conversations_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}

# Save learning memory
def save_learning_memory(memory):
    # Convert defaultdict to dict for JSON serialization
    if isinstance(memory["similar_queries"], defaultdict):
        memory["similar_queries"] = dict(memory["similar_queries"])
    
    with open(LEARNING_MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# Parse and sanitize markdown - DISABLED FOR SAFETY
def parse_markdown(text):
    """
    Parse markdown text - DISABLED to prevent browser hanging
    تحليل نص markdown - معطل لمنع تجميد المتصفح
    """
    # ALWAYS return plain text to prevent browser crashes
    # دائماً إرجاع نص عادي لمنع تعطل المتصفح
    return text  # No processing - just return as is

def strip_all_formatting(text):
    """
    Remove all formatting symbols from text to prevent browser issues
    إزالة جميع رموز التنسيق من النص لمنع مشاكل المتصفح
    """
    import re
    
    # Remove all markdown symbols
    text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', ''), text)
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'\*\*([^*]*)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]*)\*', r'\1', text)
    text = re.sub(r'_([^_]*)_', r'\1', text)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    
    return text

# Initialize custom titles global variable
_custom_titles = {}

# Enhanced load function to include custom titles
def init_conversation_memory_with_titles():
    global _custom_titles
    if os.path.exists(CONVERSATION_MEMORY_FILE):
        with open(CONVERSATION_MEMORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Handle both old and new format
            if isinstance(data, dict) and "conversations" in data:
                _custom_titles = data.get("custom_titles", {})
                return data["conversations"]
            else:
                # Old format - just conversations
                _custom_titles = {}
                return data
    else:
        _custom_titles = {}
        return {}

# Enhanced save function to include custom titles
def save_conversation_memory_with_titles(memory, custom_titles):
    data_to_save = {
        "conversations": memory,
        "custom_titles": custom_titles
    }
    with open(CONVERSATION_MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)

# Load enhanced memory systems
conversation_memory = init_conversation_memory_with_titles()
learning_memory = init_learning_memory()
user_profiles = init_user_profile_memory()  # Initialize user profiles for long-term memory

if isinstance(learning_memory["similar_queries"], dict):
    learning_memory["similar_queries"] = defaultdict(list, learning_memory["similar_queries"])

# Firebase helper functions
def get_user_id_from_session():
    """Get user ID from session or request headers"""
    # In production, you would extract this from Firebase Auth token
    # For now, we'll use a simple session-based approach
    user_id = session.get('user_id')
    if not user_id:
        # Try to get from Authorization header (Firebase ID token)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            decoded_token = verify_firebase_token(token)
            if decoded_token:
                user_id = decoded_token.get('uid')
                session['user_id'] = user_id
    
    return user_id or 'anonymous'

def clean_firebase_key(key):
    """Clean key for Firebase compatibility by removing invalid characters"""
    # Firebase doesn't allow: . $ # [ ] / 
    # Replace dots and other invalid characters with underscores
    return key.replace('.', '_').replace('$', '_').replace('#', '_').replace('[', '_').replace(']', '_').replace('/', '_')

# ============================================================================
# FIREBASE DATABASE FUNCTIONS - وظائف قاعدة بيانات Firebase
# ============================================================================

def save_conversation_to_firebase(user_id, conversation_id, conversation_data):
    """Save conversation data directly to Firebase under user ID"""
    if not firebase_initialized or user_id == 'anonymous':
        return False
    
    try:
        # Clean conversation_id for Firebase compatibility
        clean_conversation_id = clean_firebase_key(conversation_id)
        
        # Save conversation directly under the user ID path
        ref = db.reference(f'{user_id}/conversations/{clean_conversation_id}')
        ref.set(conversation_data)
        print(f"🔥 Conversation {clean_conversation_id} saved to Firebase for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error saving conversation to Firebase: {e}")
        return False

def get_conversations_from_firebase(user_id):
    """Get all conversations for a user from Firebase"""
    if not firebase_initialized or user_id == 'anonymous':
        return {}
    
    try:
        # Get conversations directly from user ID path
        ref = db.reference(f'{user_id}/conversations')
        conversations = ref.get() or {}
        print(f"📥 Retrieved {len(conversations)} conversations from Firebase for user {user_id}")
        return conversations
    except Exception as e:
        print(f"❌ Error getting conversations from Firebase: {e}")
        return {}

def save_user_profile_to_firebase(user_id, profile_data):
    """Save user profile data to Firebase"""
    if not firebase_initialized or user_id == 'anonymous':
        return False
    
    try:
        ref = db.reference(f'users/{user_id}/profile')
        ref.update(profile_data)
        print(f"✅ Profile saved to Firebase for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error saving profile to Firebase: {e}")
        return False

def get_user_profile_from_firebase(user_id):
    """Get user profile data from Firebase"""
    if not firebase_initialized or user_id == 'anonymous':
        return {}
    
    try:
        ref = db.reference(f'users/{user_id}/profile')
        profile = ref.get() or {}
        return profile
    except Exception as e:
        print(f"❌ Error getting profile from Firebase: {e}")
        return {}

def save_custom_title_to_firebase(user_id, conversation_id, title):
    """Save custom conversation title to Firebase"""
    if not firebase_initialized or user_id == 'anonymous':
        return False
    
    try:
        # Clean conversation_id for Firebase compatibility
        clean_conversation_id = clean_firebase_key(conversation_id)
        
        # Save custom title directly under user ID path
        ref = db.reference(f'{user_id}/customTitles/{clean_conversation_id}')
        ref.set(title)
        print(f"✅ Custom title saved to Firebase for conversation {clean_conversation_id}")
        return True
    except Exception as e:
        print(f"❌ Error saving custom title to Firebase: {e}")
        return False

def get_custom_titles_from_firebase(user_id):
    """Get all custom titles for a user from Firebase"""
    if not firebase_initialized or user_id == 'anonymous':
        return {}
    
    try:
        # Get custom titles directly from user ID path
        ref = db.reference(f'{user_id}/customTitles')
        titles = ref.get() or {}
        return titles
    except Exception as e:
        print(f"❌ Error getting custom titles from Firebase: {e}")
        return {}

def delete_conversation_from_firebase(user_id, conversation_id):
    """Delete conversation from Firebase"""
    if not firebase_initialized or user_id == 'anonymous':
        return False
    
    try:
        # Clean conversation_id for Firebase compatibility
        clean_conversation_id = clean_firebase_key(conversation_id)
        
        # Delete conversation directly from user ID path
        conv_ref = db.reference(f'{user_id}/conversations/{clean_conversation_id}')
        conv_ref.delete()
        
        # Delete custom title if exists
        title_ref = db.reference(f'{user_id}/customTitles/{clean_conversation_id}')
        title_ref.delete()
        
        print(f"✅ Conversation {clean_conversation_id} deleted from Firebase")
        return True
    except Exception as e:
        print(f"❌ Error deleting conversation from Firebase: {e}")
        return False

def migrate_local_data_to_firebase(user_id):
    """Migrate existing local conversation data to Firebase for a specific user"""
    if not firebase_initialized or user_id == 'anonymous':
        return False
    
    try:
        migrated_count = 0
        
        # Load local conversation memory
        local_conversations = init_conversation_memory_with_titles()
        
        # Filter conversations for this user
        user_conversations = {}
        for conv_id, conv_data in local_conversations.items():
            if conv_id.startswith(f"conv_{user_id}_") or conv_id == user_id:
                user_conversations[conv_id] = conv_data
                migrated_count += 1
        
        # Save to Firebase
        if user_conversations:
            ref = db.reference(f'users/{user_id}/conversations')
            ref.set(user_conversations)
            
            # Also migrate custom titles
            global _custom_titles
            user_titles = {k: v for k, v in _custom_titles.items() 
                          if k.startswith(f"conv_{user_id}_") or k == user_id}
            
            if user_titles:
                title_ref = db.reference(f'users/{user_id}/customTitles')
                title_ref.set(user_titles)
        
        print(f"✅ Migrated {migrated_count} conversations to Firebase for user {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating data to Firebase: {e}")
        return False

def save_learning_data_to_firebase(user_id, learning_data):
    """Save learning data to Firebase"""
    if not firebase_initialized:
        return False
    
    try:
        ref = db.reference(f'users/{user_id}/learning')
        ref.set(learning_data)
        return True
    except Exception as e:
        print(f"Error saving learning data to Firebase: {e}")
        return False

def get_learning_data_from_firebase(user_id):
    """Get learning data for a user from Firebase"""
    if not firebase_initialized:
        return {}
    
    try:
        ref = db.reference(f'users/{user_id}/learning')
        return ref.get() or {}
    except Exception as e:
        print(f"Error getting learning data from Firebase: {e}")
        return {}

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For development, we'll skip authentication check
        # In production, you would verify Firebase token here
        return f(*args, **kwargs)
    return decorated_function

# Firebase token verification (placeholder for production)
def verify_firebase_token(token):
    """
    Verify Firebase ID token and return user information
    """
    if not firebase_initialized:
        return None
        
    try:
        from firebase_admin import auth
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

# Simple responses dictionary - both in English and Arabic
responses = {
    "greeting": [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "مرحباً! كيف يمكنني مساعدتك اليوم؟",
        "أهلاً! ماذا يمكنني أن أفعل لك؟"
    ],
    "farewell": [
        "Goodbye! Have a nice day!",
        "See you later!",
        "وداعاً! أتمنى لك يوماً سعيداً!",
        "إلى اللقاء!"
    ],
    "thanks": [
        "You're welcome!",
        "Happy to help!",
        "لا شكر على واجب!",
        "سعيد بالمساعدة!"
    ],
    "unknown": [
        "I'm not sure I understand. Can you rephrase that? If my response wasn't helpful, you can teach me by saying 'Learn: [correct response]'",
        "Hmm, I'm not sure about that. Can you try asking differently? You can teach me by saying 'Learn: [correct response]'",
        "لست متأكداً من فهمي. هل يمكنك إعادة صياغة ذلك؟ إذا لم تكن إجابتي مفيدة، يمكنك تعليمي بقول 'تعلم: [الرد الصحيح]'",
        "همم، لست متأكداً من ذلك. هل يمكنك المحاولة بطريقة مختلفة؟ يمكنك تعليمي بقول 'تعلم: [الرد الصحيح]'"
    ],
    "code": [
        "I can help you with basic code examples! Here's a simple example:\n\nFunction to calculate area:\n----------\nfunction calculateArea(width, height) {\n    return width * height;\n}\n\nconsole.log(calculateArea(5, 3)); // Output: 15\n----------\n\nWhat specific programming language or concept would you like help with?",
        "يمكنني مساعدتك بأمثلة كود بسيطة! إليك مثال:\n\nدالة لحساب المساحة:\n----------\nfunction calculateArea(width, height) {\n    return width * height;\n}\n\nconsole.log(calculateArea(5, 3)); // النتيجة: 15\n----------\n\nما هي لغة البرمجة أو المفهوم المحدد الذي تريد المساعدة به؟"
    ],
    "bot": [
        "I'm just a simple chatbot created with Python! I can learn from our conversations and provide basic responses. (Advanced AI features are temporarily unavailable due to quota limits)",
        "I'm a chatbot built with Python. I'm designed to improve over time by learning from interactions. (Advanced AI is temporarily unavailable)",
        "أنا مجرد روبوت محادثة بسيط تم إنشاؤه باستخدام Python! يمكنني التعلم من محادثاتنا وتقديم ردود أساسية. (الميزات المتقدمة معطلة مؤقتاً بسبب حدود الحصة)",
        "أنا روبوت محادثة تم بناؤه باستخدام Python. تم تصميمي للتحسن مع مرور الوقت من خلال التعلم من التفاعلات. (الذكاء الاصطناعي المتقدم معطل مؤقتاً)"
    ],
    "capabilities": [
        "I can chat with you in English and Arabic. I can answer simple questions, have basic conversations, and provide simple code examples. I'm also able to learn from our interactions! (Advanced AI features are temporarily unavailable)",
        "I'm a bilingual chatbot that can understand both English and Arabic. I have a basic understanding of conversation flow and I learn from our chats. (Advanced AI is temporarily unavailable)",
        "يمكنني التحدث معك باللغتين الإنجليزية والعربية. يمكنني الإجابة على الأسئلة البسيطة وإجراء محادثات أساسية وتقديم أمثلة كود بسيطة. كما يمكنني التعلم من تفاعلاتنا! (الميزات المتقدمة معطلة مؤقتاً)",
        "أنا روبوت محادثة ثنائي اللغة يمكنه فهم كل من اللغة الإنجليزية والعربية. لدي فهم أساسي لتدفق المحادثة وأتعلم من محادثاتنا. (الذكاء الاصطناعي المتقدم معطل مؤقتاً)"
    ],
    "weather": [
        "I'm sorry, I don't have access to real-time weather data. You would need to connect to a weather API for that feature.",
        "أنا آسف، ليس لدي وصول إلى بيانات الطقس في الوقت الفعلي. ستحتاج إلى الاتصال بواجهة برمجة تطبيقات الطقس لهذه الميزة."
    ],
    "time": [
        f"The current server time is {time.strftime('%H:%M:%S')}",
        f"الوقت الحالي للخادم هو {time.strftime('%H:%M:%S')}"
    ],
    "date": [
        f"Today is {time.strftime('%Y-%m-%d')}",
        f"اليوم هو {time.strftime('%Y-%m-%d')}"
    ],
    "name": [
        "My name is ChatBot. What's yours?",
        "I'm ChatBot, your AI assistant.",
        "اسمي ChatBot. ما هو اسمك؟",
        "أنا ChatBot، مساعدك الذكي."
    ],
    "help": [
        "I can chat with you in English or Arabic. You can ask me about myself, the time, date, basic code examples, or just have a casual conversation! If I make a mistake, you can teach me by saying 'Learn: [correct response]'",
        "يمكنني التحدث معك باللغة الإنجليزية أو العربية. يمكنك أن تسألني عن نفسي، الوقت، التاريخ، أمثلة كود بسيطة، أو مجرد إجراء محادثة عادية! إذا ارتكبت خطأ، يمكنك تعليمي بقول 'تعلم: [الرد الصحيح]'"
    ],
    "learning": [
        "I've learned this response. Thank you for teaching me!",
        "Got it! I'll remember this for next time.",
        "لقد تعلمت هذا الرد. شكراً لتعليمي!",
        "فهمت! سأتذكر هذا للمرة القادمة."
    ],
    "self_improvement": [
        "I'm designed to learn from our conversations. The more we chat, the better I get!",
        "أنا مصمم للتعلم من محادثاتنا. كلما تحدثنا أكثر، أصبحت أفضل!"
    ],
    "gemini": [
        "Advanced AI features are temporarily unavailable due to quota limits. Using basic responses...",
        "الميزات المتقدمة للذكاء الاصطناعي معطلة مؤقتاً بسبب حدود الحصة. استخدام الردود الأساسية..."
    ],
    "markdown": [
        "Markdown formatting is currently disabled to prevent browser issues. Text is displayed as plain text.",
        "تنسيق Markdown معطل حالياً لمنع مشاكل المتصفح. النص يعرض كنص عادي."
    ]
}

# Pattern matching rules
patterns = {
    "greeting": r"(hello|hi|hey|مرحبا|أهلا|السلام عليكم)",
    "farewell": r"(goodbye|bye|see you|وداعا|مع السلامة)",
    "thanks": r"(thank|thanks|شكرا|شكراً)",
    "bot": r"(who are you|what are you|من أنت|ما هو أنت)",
    "capabilities": r"(what can you do|what are your capabilities|ماذا يمكنك أن تفعل|ما هي قدراتك)",
    "weather": r"(weather|forecast|temperature|الطقس|درجة الحرارة)",
    "time": r"(time|الوقت|الساعة)",
    "date": r"(date|today|التاريخ|اليوم)",
    "name": r"(your name|اسمك)",
    "help": r"(help|مساعدة)",
    "learning": r"(learn:|تعلم:)",
    "self_improvement": r"(learn from mistakes|self-learning|improve yourself|تعلم من أخطائك|التعلم الذاتي|تحسين نفسك)",
    "markdown": r"(markdown|formatting|تنسيق|ماركداون)",
    "code": r"(code|script|function|class|example|how to|implement|programming|algorithm|syntax|write a|create a|build a|javascript|python|css|html|java|كود|برمجة|مثال|كيف|اكتب|انشئ|صمم|طور|دالة|فئة|كلاس|سكريبت|خوارزمية|تطبيق|موقع|تصميم)"
}

# Language detection (simple version)
def detect_language(text):
    # Arabic unicode range
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    if arabic_pattern.search(text):
        return 'arabic'
    return config.DEFAULT_LANGUAGE

# Preprocess text
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

# Get conversation history for context
def get_conversation_context(session_id, limit=None):
    if not limit:
        limit = config.CONTEXT_MESSAGES
        
    if session_id in conversation_memory and len(conversation_memory[session_id]) > 0:
        # Get the most recent messages
        recent_messages = conversation_memory[session_id][-limit:]
        
        # Format the context
        context = []
        for msg in recent_messages:
            role = "user" if msg["role"] == "user" else "assistant"
            content = msg["message"]
            context.append({"role": role, "parts": [content]})
        
        return context
    
    return []

def detect_code_request(user_input):
    """
    Detect if user is asking for code examples
    اكتشاف إذا كان المستخدم يطلب أمثلة كود
    """
    code_keywords = [
        # English
        'code', 'script', 'function', 'class', 'example', 'how to', 'implement', 
        'programming', 'algorithm', 'syntax', 'write a', 'create a', 'build a',
        'javascript', 'python', 'css', 'html', 'java', 'c++', 'php', 'sql',
        
        # Arabic
        'كود', 'برمجة', 'مثال', 'كيف', 'اكتب', 'انشئ', 'صمم', 'طور', 'دالة',
        'فئة', 'كلاس', 'سكريبت', 'خوارزمية', 'تطبيق', 'موقع', 'تصميم'
    ]
    
    user_input_lower = user_input.lower()
    return any(keyword in user_input_lower for keyword in code_keywords)

def enhance_code_response(response_text, user_input):
    """
    Enhance code responses with clean Markdown format
    تحسين استجابات الكود بتنسيق Markdown نظيف
    """
    # Return clean response without modifications for natural Markdown rendering
    # إرجاع الاستجابة نظيفة بدون تعديلات لعرض Markdown الطبيعي
    
    # Just return the original response - let Markdown work naturally
    return response_text

# This function was removed to avoid duplication

# Find similar questions in the learning memory
def find_similar_question(processed_input):
    for question, answers in learning_memory.get("user_corrections", {}).items():
        if processed_input in question or question in processed_input:
            # If the input is similar to a question we've learned from
            return random.choice(answers)
    return None

# Process learning requests
def process_learning(user_input, session_id):
    # Check if it's a learning command
    learning_pattern = re.compile(r'^(learn:|تعلم:)\s*(.*)', re.IGNORECASE)
    match = learning_pattern.match(user_input)
    
    if match:
        # Get the correct response from the user
        correct_response = match.group(2).strip()
        
        if not correct_response:
            return "Please provide a response to learn.", True
        
        # Get the last message from the conversation
        last_message = None
        if session_id in conversation_memory and len(conversation_memory[session_id]) >= 2:
            last_messages = conversation_memory[session_id][-2:]
            # Find the user's message that needed correction
            for msg in last_messages:
                if msg["role"] == "user" and msg["message"] != user_input:
                    last_message = msg["message"]
                    break
        
        if last_message:
            # Store the learned response
            processed_last_message = preprocess_text(last_message)
            
            if "user_corrections" not in learning_memory:
                learning_memory["user_corrections"] = {}
            
            if processed_last_message in learning_memory["user_corrections"]:
                if correct_response not in learning_memory["user_corrections"][processed_last_message]:
                    learning_memory["user_corrections"][processed_last_message].append(correct_response)
            else:
                learning_memory["user_corrections"][processed_last_message] = [correct_response]
            
            # Save the updated learning memory
            save_learning_memory(learning_memory)
            
            # Return a confirmation message
            language = detect_language(user_input)
            if language == 'arabic':
                return random.choice(responses["learning"][2:]), True
            else:
                return random.choice(responses["learning"][:2]), True
        else:
            return "I couldn't find the message to correct. Can you try again?", True
    
    return None, False

# Record message in conversation memory
def record_message(session_id, role, message, file_data=None):
    """
    Record a message to the conversation - Firebase First Approach
    سجل رسالة في المحادثة - نهج Firebase أولاً
    """
    user_id = get_user_id_from_session()
    
    message_data = {
        "role": role,
        "message": message,
        "timestamp": time.time()
    }
    
    # Add file data if present
    if file_data:
        message_data["file_data"] = file_data
    
    # === FIREBASE FIRST APPROACH ===
    if firebase_initialized and user_id != 'anonymous':
        # Load existing conversation from Firebase
        firebase_conversation = get_conversations_from_firebase(user_id).get(session_id, [])
        
        # Add new message
        firebase_conversation.append(message_data)
        
        # Limit conversation history to last 50 messages
        if len(firebase_conversation) > 50:
            firebase_conversation = firebase_conversation[-50:]
        
        # Save back to Firebase
        success = save_conversation_to_firebase(user_id, session_id, firebase_conversation)
        if success:
            print(f"🔥 Message saved to Firebase for user {user_id}")
            
            # Update local memory for current session (cache)
            conversation_memory[session_id] = firebase_conversation
            return
    
    # === FALLBACK TO LOCAL STORAGE ===
    # For anonymous users or when Firebase is not available
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    
    conversation_memory[session_id].append(message_data)
    
    # Limit conversation history to last 30 messages for local storage
    if len(conversation_memory[session_id]) > 30:
        conversation_memory[session_id] = conversation_memory[session_id][-30:]
    
    # Save to user-specific local storage as backup
    if user_id != 'anonymous':
        save_user_conversation_locally(user_id, session_id, conversation_memory[session_id])
        print(f"💾 Message saved locally for user {user_id}")
    else:
        # Save to global memory for anonymous users
        save_conversation_memory(conversation_memory)
        print(f"💾 Anonymous message saved locally")

# Update the frequency of matched patterns
def update_pattern_frequency(intent):
    if intent not in learning_memory["pattern_frequency"]:
        learning_memory["pattern_frequency"][intent] = 0
    
    learning_memory["pattern_frequency"][intent] += 1
    save_learning_memory(learning_memory)

def get_response(user_input, session_id):
    """
    Enhanced response generation with better context awareness and intelligent length adaptation
    توليد استجابة محسن مع وعي أفضل بالسياق وتكيف ذكي للطول
    """
    # Check if message is too long
    if len(user_input) > config.MAX_MESSAGE_LENGTH:
        return "Your message is too long. Please keep it under {} characters.".format(
            config.MAX_MESSAGE_LENGTH
        )
    
    # First, check if this is a learning request
    learning_response, is_learning = process_learning(user_input, session_id)
    if is_learning:
        return learning_response
    
    # Record user's message in conversation memory
    record_enhanced_message(session_id, "user", user_input)
    
    # Preprocess input
    preprocessed_input = preprocess_text(user_input)
    
    # Check for learned responses first (highest priority)
    learned_response = find_similar_question(preprocessed_input)
    if learned_response:
        record_enhanced_message(session_id, "bot", learned_response)
        return learned_response
    
    # Update time-based responses
    responses["time"] = [
        f"The current server time is {time.strftime('%H:%M:%S')}",
        f"الوقت الحالي للخادم هو {time.strftime('%H:%M:%S')}"
    ]
    responses["date"] = [
        f"Today is {time.strftime('%Y-%m-%d')}",
        f"اليوم هو {time.strftime('%Y-%m-%d')}"
    ]
    
    # Detect language and determine response style needed
    language = detect_language(user_input)
    
    # Analyze user input for response length requirements
    requires_detailed_response = detect_detailed_response_needed(user_input)
    
    # Check for markdown inquiry (disabled feature)
    if re.search(patterns["markdown"], preprocessed_input, re.IGNORECASE):
        if language == 'arabic':
            markdown_response = responses["markdown"][1]
        else:
            markdown_response = responses["markdown"][0]
        record_enhanced_message(session_id, "bot", markdown_response)
        return markdown_response
    
    # Try Gemini for complex queries that need detailed responses
    if gemini_available and (requires_detailed_response or config.USE_GEMINI_AFTER_ATTEMPTS == 0):
        try:
            gemini_response = get_context_aware_response(user_input, session_id)
            if gemini_response:
                # Apply length adaptation based on query type
                adapted_response = adapt_response_length(gemini_response, user_input, language)
                record_enhanced_message(session_id, "bot", adapted_response)
                return adapted_response
        except Exception as e:
            print(f"Gemini error: {e}")
            # Continue to pattern matching if Gemini fails
    
    # Check for simple patterns that can be handled locally
    for intent in ["greeting", "farewell", "thanks", "time", "date", "name", "help", "bot", "capabilities"]:
        pattern = patterns.get(intent)
        if pattern and re.search(pattern, preprocessed_input, re.IGNORECASE):
            # Update pattern frequency for learning
            update_pattern_frequency(intent)
            
            # Get appropriate language response
            if language == 'arabic':
                # Choose Arabic responses (indices 2 and up)
                filtered_responses = [r for i, r in enumerate(responses[intent]) if i >= 2]
                if not filtered_responses:
                    # Fallback to first available response
                    filtered_responses = [responses[intent][-1]] if responses[intent] else ["عذراً، لا يمكنني المساعدة"]
            else:
                # Choose English responses (indices 0 and 1)
                filtered_responses = [r for i, r in enumerate(responses[intent]) if i < 2]
                if not filtered_responses:
                    # Fallback to first available response
                    filtered_responses = [responses[intent][0]] if responses[intent] else ["Sorry, I can't help"]
            
            if filtered_responses:
                selected_response = random.choice(filtered_responses)
                record_enhanced_message(session_id, "bot", selected_response)
                return selected_response
    
    # Handle code requests with appropriate detail level
    if detect_code_request(user_input):
        if requires_detailed_response:
            # Try Gemini for detailed code explanations
            if gemini_available:
                try:
                    gemini_response = get_context_aware_response(user_input, session_id)
                    if gemini_response:
                        adapted_response = adapt_response_length(gemini_response, user_input, language)
                        record_enhanced_message(session_id, "bot", adapted_response)
                        return adapted_response
                except Exception as e:
                    print(f"Gemini code error: {e}")
        
        # Fallback to simple code response
        if language == 'arabic':
            code_response = responses["code"][1] if len(responses["code"]) > 1 else responses["code"][0]
        else:
            code_response = responses["code"][0]
        
        record_enhanced_message(session_id, "bot", code_response)
        return code_response
    
    # For all other queries, try Gemini with context awareness
    if gemini_available:
        try:
            gemini_response = get_context_aware_response(user_input, session_id)
            if gemini_response:
                adapted_response = adapt_response_length(gemini_response, user_input, language)
                record_enhanced_message(session_id, "bot", adapted_response)
                return adapted_response
        except Exception as e:
            print(f"Gemini general error: {e}")
    
    # If all else fails, return contextual unknown response
    if language == 'arabic':
        unknown_response = random.choice(responses["unknown"][2:])
    else:
        unknown_response = random.choice(responses["unknown"][:2])
    
    record_enhanced_message(session_id, "bot", unknown_response)
    return unknown_response

def detect_detailed_response_needed(user_input):
    """
    Detect if the user is asking for a detailed response or simple answer
    كشف ما إذا كان المستخدم يطلب إجابة مفصلة أم بسيطة
    """
    detailed_indicators = [
        # English
        'explain', 'how to', 'tutorial', 'guide', 'detailed', 'step by step', 
        'example', 'examples', 'create', 'build', 'develop', 'implement',
        'write article', 'write code', 'full code', 'complete', 'comprehensive',
        'table', 'list', 'comparison', 'pros and cons', 'advantages', 'disadvantages',
        
        # Arabic  
        'اشرح', 'كيف', 'دليل', 'تفصيلي', 'مفصل', 'خطوة بخطوة',
        'مثال', 'أمثلة', 'انشئ', 'اكتب', 'طور', 'اصنع', 'ابني',
        'كود كامل', 'مقال', 'جدول', 'قائمة', 'مقارنة', 'مميزات', 'عيوب'
    ]
    
    simple_indicators = [
        # English
        'what is', 'what are', 'yes or no', 'true or false', 'simply',
        'briefly', 'short', 'quick', 'just tell me', 'only',
        
        # Arabic
        'ما هو', 'ما هي', 'نعم أم لا', 'صح أم خطأ', 'ببساطة',
        'بإختصار', 'قصير', 'سريع', 'فقط قل لي', 'فقط'
    ]
    
    user_input_lower = user_input.lower()
    
    # Check for simple indicators first (higher priority)
    if any(indicator in user_input_lower for indicator in simple_indicators):
        return False
    
    # Check for detailed indicators
    if any(indicator in user_input_lower for indicator in detailed_indicators):
        return True
    
    # Default based on length of question
    return len(user_input.split()) > 8  # More than 8 words suggests detailed query

def adapt_response_length(response, user_input, language):
    """
    Adapt response length based on user's query type
    تكييف طول الاستجابة بناءً على نوع استعلام المستخدم
    """
    requires_detailed = detect_detailed_response_needed(user_input)
    
    if not requires_detailed:
        # User wants brief answer - truncate if too long
        lines = response.split('\n')
        if len(lines) > 5:  # If more than 5 lines, summarize
            if language == 'arabic':
                brief_response = '\n'.join(lines[:3]) + '\n\n[إجابة مختصرة - اطلب التفاصيل إذا كنت تريد المزيد]'
            else:
                brief_response = '\n'.join(lines[:3]) + '\n\n[Brief answer - ask for details if you want more]'
            return brief_response
        elif len(response) > 500:  # If too long, cut it short
            if language == 'arabic':
                return response[:400] + '...\n\n[اطلب التفاصيل إذا كنت تريد المزيد]'
            else:
                return response[:400] + '...\n\n[Ask for details if you want more]'
    
    # For detailed responses, ensure good length but not too long to avoid browser issues
    if len(response) > config.MAX_CODE_BLOCK_SIZE:
        if language == 'arabic':
            return response[:config.MAX_CODE_BLOCK_SIZE] + '\n\n[تم اختصار الرد لمنع مشاكل المتصفح - يمكنك طلب جزء محدد للمزيد]'
        else:
            return response[:config.MAX_CODE_BLOCK_SIZE] + '\n\n[Response truncated to prevent browser issues - you can ask for specific part for more]'
    
    return response

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
@login_required
def home():
    # Generate a unique session ID if one doesn't exist
    if 'session_id' not in session:
        session['session_id'] = str(time.time())
    
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/save_user_session', methods=['POST'])
def save_user_session():
    """Save user session data from Firebase authentication"""
    try:
        data = request.json
        user_id = data.get('user_id')
        email = data.get('email')
        name = data.get('name')
        
        if user_id:
            session['user_id'] = user_id
            session['user_email'] = email
            session['user_name'] = name
            print(f"✅ User session saved: {user_id} ({email})")
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Missing user_id"}), 400
    except Exception as e:
        print(f"❌ Error saving user session: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    session_id = request.json.get('session_id', 'default')
    
    if not user_input.strip():
        return jsonify({'error': 'Empty message'}), 400
    
    try:
        # Record user message
        record_message(session_id, 'user', user_input)
        
        # Generate response
        bot_response = get_response(user_input, session_id)
        
        # Truncate response if too long to prevent browser crashes
        if len(bot_response) > config.MAX_RESPONSE_LENGTH:
            if detect_language(user_input) == "arabic":
                bot_response = bot_response[:config.MAX_RESPONSE_LENGTH] + "\n\n[تم اقتطاع الاستجابة لتجنب تعليق المتصفح]"
            else:
                bot_response = bot_response[:config.MAX_RESPONSE_LENGTH] + "\n\n[Response truncated to prevent browser hanging]"
        
        # Convert session_id to conversation_id format if needed
        if not session_id.startswith('conv-'):
            active_conversation_id = f"conv-{session_id}"
        else:
            active_conversation_id = session_id
        
        # Record bot response
        record_message(active_conversation_id, 'assistant', bot_response)
        
        # Skip markdown processing to prevent browser hanging
        bot_response_html = bot_response  # Use plain text instead of HTML
        
        # Save to Firebase if user is authenticated
        user_id = get_user_id_from_session()
        if user_id != 'anonymous' and firebase_initialized:
            try:
                # Get the full conversation
                conversation_data = conversation_memory.get(active_conversation_id, [])
                if conversation_data:
                    save_conversation_to_firebase(user_id, active_conversation_id, conversation_data)
                    print(f"🔥 Saved conversation {active_conversation_id} to Firebase for user {user_id}")
            except Exception as e:
                print(f"❌ Error saving to Firebase: {e}")
        
        return jsonify({
            'response': bot_response,
            'response_html': bot_response_html,
            'has_markdown': False,  # Always false now to prevent browser issues
            'conversation_id': active_conversation_id
        })
        
    except Exception as e:
        print(f"Error in chat route: {e}")
        traceback.print_exc()
        
        if detect_language(user_input) == "arabic":
            error_msg = "عذراً، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى."
        else:
            error_msg = "Sorry, an error occurred while processing your request. Please try again."
        
        return jsonify({'error': error_msg}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    # Return statistics about the chatbot's learning
    stats = {
        "learned_responses": len(learning_memory.get("user_corrections", {})),
        "conversation_sessions": len(conversation_memory),
        "popular_topics": sorted(learning_memory.get("pattern_frequency", {}).items(), 
                               key=lambda x: x[1], reverse=True)[:5],
        "gemini_available": gemini_available,
        "markdown_enabled": config.ENABLE_MARKDOWN
    }
    return jsonify(stats)

# Get statistics
@app.route('/get_statistics', methods=['GET'])
def get_statistics():
    stats = {
        "learned_responses": len(learning_memory["user_corrections"]),
        "conversation_sessions": len(conversation_memory),
        "popular_topics": get_popular_topics(),
        "stats_over_time": get_stats_over_time()
    }
    return jsonify(stats)

def get_popular_topics(top_n=5):
    # Get the top N most frequent intents
    if not learning_memory["pattern_frequency"]:
        return []
    
    sorted_patterns = sorted(learning_memory["pattern_frequency"].items(), 
                            key=lambda x: x[1], reverse=True)
    return [p[0] for p in sorted_patterns[:top_n]]

def get_stats_over_time():
    """Generate statistics over time for charting"""
    # This is a simplified version - in a real app, you'd store daily stats
    # For this demo, we'll synthesize some data
    
    stats = []
    # Get data for the last 7 days
    today = time.time()
    
    for i in range(7):
        day_timestamp = today - (i * 86400)  # 86400 seconds in a day
        day_date = time.strftime("%Y-%m-%d", time.localtime(day_timestamp))
        
        # In a real implementation, you would query your database
        # Here we'll simulate with random growth
        conversations_count = max(0, len(conversation_memory) - i * 2)
        learned_count = max(0, len(learning_memory["user_corrections"]) - i)
        
        stats.append({
            "date": day_date,
            "conversations": conversations_count,
            "learned": learned_count
        })
    
    # Reverse to get chronological order
    return list(reversed(stats))

# Get all conversations - Firebase First Approach
@app.route('/get_conversations', methods=['GET'])
def get_conversations():
    """
    Get all conversations for the current user - Firebase First
    احصل على جميع المحادثات للمستخدم الحالي - Firebase أولاً
    """
    user_id = get_user_id_from_session()
    result = {"conversations": []}
    
    # Security: Only return conversations for the current user
    if user_id == 'anonymous':
        # For anonymous users, only show conversations in current session
        session_conversations = {}
        session_id = session.get('session_id')
        if session_id and session_id in conversation_memory:
            session_conversations[session_id] = conversation_memory[session_id]
        all_conversations = session_conversations
        custom_titles = {}
    else:
        # === FIREBASE FIRST APPROACH ===
        all_conversations = {}
        custom_titles = {}
        
        if firebase_initialized:
            # 1. Load conversations from Firebase
            firebase_conversations = get_conversations_from_firebase(user_id)
            if firebase_conversations:
                all_conversations.update(firebase_conversations)
                print(f"🔥 Loaded {len(firebase_conversations)} conversations from Firebase for user {user_id}")
            
            # 2. Load custom titles from Firebase
            firebase_titles = get_custom_titles_from_firebase(user_id)
            if firebase_titles:
                custom_titles.update(firebase_titles)
                print(f"🏷️ Loaded {len(firebase_titles)} custom titles from Firebase for user {user_id}")
        
        # === FALLBACK TO LOCAL STORAGE ===
        if not all_conversations:
            # Load from local user storage as fallback
            local_conversations = load_user_conversations_locally(user_id)
            if local_conversations:
                all_conversations.update(local_conversations)
                print(f"💾 Fallback: Loaded {len(local_conversations)} conversations from local storage for user {user_id}")
            
            # Use global custom titles as fallback
            global _custom_titles
            for conv_id, title in _custom_titles.items():
                if conv_id.startswith(f"conv_{user_id}_"):
                    custom_titles[conv_id] = title
        
        # 3. Include conversations from current session that belong to this user
        for session_id, conversation in conversation_memory.items():
            if session_id.startswith(f"conv_{user_id}_") and session_id not in all_conversations:
                all_conversations[session_id] = conversation
                print(f"📝 Added current session conversation: {session_id}")
    
    # Process conversations for response
    for session_id, conversation in all_conversations.items():
        if not conversation:
            continue
        
        # Ensure conversation is a list of dictionaries
        if not isinstance(conversation, list):
            print(f"⚠️ Invalid conversation format for {session_id}: {type(conversation)}")
            continue
        
        # Check if there's a custom title (Firebase first, then local)
        title = custom_titles.get(session_id)
        if not title and user_id == 'anonymous':
            title = _custom_titles.get(session_id)
        
        if not title:
            # Get the first message from user as title
            try:
                first_user_message = next((msg["message"] for msg in conversation if isinstance(msg, dict) and msg.get("role") == "user"), "")
                title = first_user_message[:30] + "..." if len(first_user_message) > 30 else first_user_message
            except (TypeError, KeyError) as e:
                print(f"⚠️ Error processing conversation {session_id}: {e}")
                title = "محادثة جديدة | New conversation"
        
        # Get the last message as preview
        try:
            if conversation and isinstance(conversation[-1], dict):
                last_message = conversation[-1].get("message", "")
                preview = last_message[:30] + "..." if len(last_message) > 30 else last_message
            else:
                preview = "لا توجد رسائل | No messages"
        except (IndexError, TypeError):
            preview = "لا توجد رسائل | No messages"
        
        # Get timestamp safely
        try:
            if conversation and isinstance(conversation[-1], dict):
                timestamp = conversation[-1].get("timestamp", 0)
            else:
                timestamp = 0
        except (IndexError, TypeError):
            timestamp = 0
        
        result["conversations"].append({
            "id": session_id,
            "title": title or "محادثة جديدة | New conversation",
            "preview": preview or "لا توجد رسائل | No messages",
            "timestamp": timestamp
        })
    
    # Sort by timestamp, newest first
    result["conversations"].sort(key=lambda x: x["timestamp"], reverse=True)
    
    print(f"📋 Returning {len(result['conversations'])} conversations for user {user_id}")
    return jsonify(result)

# Get a specific conversation
@app.route('/get_conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    user_id = get_user_id_from_session()
    
    # Security: Check if user has access to this conversation
    has_access = False
    conversation_data = None
    
    if user_id == 'anonymous':
        # Anonymous users can only access conversations in their session
        session_id = session.get('session_id')
        if conversation_id == session_id and conversation_id in conversation_memory:
            has_access = True
            conversation_data = conversation_memory[conversation_id]
    else:
        # Authenticated users can access their own conversations
        # Check if conversation belongs to user (by ID pattern or Firebase)
        if conversation_id.startswith(f"conv_{user_id}_"):
            has_access = True
            conversation_data = conversation_memory.get(conversation_id)
        
        # Also check local user conversations file
        if not has_access:
            user_conversations = load_user_conversations_locally(user_id)
            if conversation_id in user_conversations:
                has_access = True
                conversation_data = user_conversations[conversation_id]
                # Load into memory for current session
                conversation_memory[conversation_id] = conversation_data
        
        # Also check Firebase for user's conversations
        if not has_access and firebase_initialized:
            firebase_conversations = get_conversations_from_firebase(user_id)
            # Check both original and cleaned conversation_id
            clean_conversation_id = clean_firebase_key(conversation_id)
            if conversation_id in firebase_conversations:
                has_access = True
                conversation_data = firebase_conversations[conversation_id]
                # Load into memory for current session
                conversation_memory[conversation_id] = conversation_data
            elif clean_conversation_id in firebase_conversations:
                has_access = True
                conversation_data = firebase_conversations[clean_conversation_id]
                # Load into memory for current session
                conversation_memory[conversation_id] = conversation_data
    
    if not has_access or not conversation_data:
        return jsonify({"error": "Conversation not found or access denied"}), 404
    
    messages = []
    
    # Handle different conversation data formats
    if isinstance(conversation_data, dict) and "messages" in conversation_data:
        # New format: {"messages": [...], "title": "...", ...}
        message_list = conversation_data["messages"]
    elif isinstance(conversation_data, list):
        # Old format: direct array of messages
        message_list = conversation_data
    else:
        return jsonify({"error": "Invalid conversation data format"}), 500
    
    for msg in message_list:
        messages.append({
            "text": msg["message"],
            "sender": "user" if msg["role"] == "user" else "bot",
            "timestamp": msg.get("timestamp", 0)
        })
    
    return jsonify({"messages": messages})

# Send message - updated endpoint 
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_input = data.get('message', '')
    conversation_id = data.get('conversation_id', '')
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    
    # Get user ID from session or Firebase token
    user_id = get_user_id_from_session()
    
    # Create session if doesn't exist
    if not conversation_id:
        # Use only integer timestamp for Firebase compatibility
        timestamp = int(time.time())
        conversation_id = f"conv_{user_id}_{timestamp}"
    
    # Initialize conversation in memory if not exists
    if conversation_id not in conversation_memory:
        conversation_memory[conversation_id] = []
        
    # Try to load from Firebase if available
    if firebase_initialized and user_id != 'anonymous':
        firebase_conversations = get_conversations_from_firebase(user_id)
        if firebase_conversations:
            # Check both original and cleaned conversation_id
            clean_conversation_id = clean_firebase_key(conversation_id)
            if conversation_id in firebase_conversations:
                conversation_memory[conversation_id] = firebase_conversations[conversation_id]
            elif clean_conversation_id in firebase_conversations:
                conversation_memory[conversation_id] = firebase_conversations[clean_conversation_id]
    
    # Process message and get response
    response = get_response(user_input, conversation_id)
    
    # No need to generate title here - will be generated when starting new conversation
    conversation_title = None
    
    # Save updated memory (Firebase save is handled in record_message)
    save_conversation_memory(conversation_memory)
    
    # Get updated stats
    stats = {
        "learned_responses": len(learning_memory.get("user_corrections", {})),
        "conversation_sessions": len(conversation_memory),
        "popular_topics": get_popular_topics()
    }
    
    return jsonify({
        "response": response,
        "conversation_id": conversation_id,
        "conversation_title": conversation_title,
        "stats": stats
    })

# Generate conversation title using AI
def generate_conversation_title(conversation_id):
    """Generate a meaningful title for the conversation using AI"""
    if conversation_id not in conversation_memory or len(conversation_memory[conversation_id]) < 1:
        return None
    
    try:
        # Get all messages from the conversation for context
        messages = conversation_memory[conversation_id]
        context = ""
        user_language = "english"  # default
        
        # Build context from all messages, but limit each message length
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            message_text = msg['message'][:150]  # Limit message length
            context += f"{role}: {message_text}\n"
            
            # Detect language from first user message
            if msg["role"] == "user" and user_language == "english":
                user_language = detect_language(message_text)
        
        # Use Gemini to generate title if available
        if gemini_available:
            if user_language == "arabic":
                prompt = f"""بناءً على هذه المحادثة، قم بإنشاء عنوان قصير ووصفي (بحد أقصى 4-6 كلمات) يلخص الموضوع الرئيسي أو السؤال. يجب أن يكون العنوان باللغة العربية.

المحادثة:
{context}

اكتب العنوان فقط، بدون أي شيء آخر. اجعله مختصراً ومفيداً."""
            else:
                prompt = f"""Based on this conversation, generate a short, descriptive title (maximum 4-6 words) that captures the main topic or question. The title should be in English.

Conversation:
{context}

Generate only the title, nothing else. Make it concise and meaningful."""
            
            try:
                response = gemini_model.generate_content(prompt)
                title = response.text.strip()
                
                # Clean up the title
                title = title.replace('"', '').replace("'", "").replace("**", "").strip()
                if len(title) > 50:
                    title = title[:47] + "..."
                
                # Remove any extra formatting or explanations
                if "\n" in title:
                    title = title.split("\n")[0].strip()
                
                return title
            except Exception as e:
                print(f"Error generating AI title: {e}")
        
        # Fallback: use first user message
        first_user_msg = next((msg["message"] for msg in messages if msg["role"] == "user"), "")
        if first_user_msg:
            title = first_user_msg[:30]
            if len(first_user_msg) > 30:
                title += "..."
            return title
        
        return "New Conversation"
        
    except Exception as e:
        print(f"Error in generate_conversation_title: {e}")
        return "New Conversation"

# Update conversation title
@app.route('/update_conversation_title', methods=['POST'])
def update_conversation_title():
    data = request.json
    conversation_id = data.get('conversation_id', '')
    new_title = data.get('title', '').strip()
    user_id = get_user_id_from_session()
    
    if not conversation_id or not new_title:
        return jsonify({"error": "Missing conversation_id or title"}), 400
    
    # Security: Check if user has access to update this conversation
    has_access = False
    
    if user_id == 'anonymous':
        # Anonymous users can only update conversations in their session
        session_id = session.get('session_id')
        if conversation_id == session_id and conversation_id in conversation_memory:
            has_access = True
    else:
        # Authenticated users can update their own conversations
        if conversation_id.startswith(f"conv_{user_id}_") and conversation_id in conversation_memory:
            has_access = True
        
        # Also check local user conversations file
        if not has_access:
            user_conversations = load_user_conversations_locally(user_id)
            if conversation_id in user_conversations:
                has_access = True
        
        # Also check Firebase for user's conversations
        if not has_access and firebase_initialized:
            firebase_conversations = get_conversations_from_firebase(user_id)
            if conversation_id in firebase_conversations:
                has_access = True
    
    if not has_access:
        return jsonify({"error": "Conversation not found or access denied"}), 404
    
    # === FIREBASE FIRST APPROACH ===
    if user_id != 'anonymous' and firebase_initialized:
        # Save to Firebase first
        success = save_custom_title_to_firebase(user_id, conversation_id, new_title)
        if success:
            print(f"🔥 Custom title saved to Firebase for conversation {conversation_id}")
            return jsonify({"success": True, "title": new_title})
    
    # === FALLBACK TO LOCAL STORAGE ===
    # Store custom titles in global variable
    global _custom_titles
    _custom_titles[conversation_id] = new_title
    
    # Save to file (we'll modify the save function to include custom titles)
    save_conversation_memory_with_titles(conversation_memory, _custom_titles)
    print(f"💾 Custom title saved locally for conversation {conversation_id}")
    
    return jsonify({"success": True, "title": new_title})

# Generate title for previous conversation when starting new one
@app.route('/generate_conversation_title', methods=['POST'])
def generate_conversation_title_endpoint():
    data = request.json
    conversation_id = data.get('conversation_id', '')
    user_id = get_user_id_from_session()
    
    if not conversation_id:
        return jsonify({"error": "Missing conversation_id"}), 400
    
    # Security: Check if user has access to this conversation
    has_access = False
    
    if user_id == 'anonymous':
        # Anonymous users can only generate titles for conversations in their session
        session_id = session.get('session_id')
        if conversation_id == session_id and conversation_id in conversation_memory:
            has_access = True
    else:
        # Authenticated users can generate titles for their own conversations
        if conversation_id.startswith(f"conv_{user_id}_") and conversation_id in conversation_memory:
            has_access = True
        
        # Also check local user conversations file
        if not has_access:
            user_conversations = load_user_conversations_locally(user_id)
            if conversation_id in user_conversations:
                has_access = True
                # Load into memory for title generation
                conversation_memory[conversation_id] = user_conversations[conversation_id]
        
        # Also check Firebase for user's conversations
        if not has_access and firebase_initialized:
            firebase_conversations = get_conversations_from_firebase(user_id)
            if conversation_id in firebase_conversations:
                has_access = True
                # Load into memory for title generation
                conversation_memory[conversation_id] = firebase_conversations[conversation_id]
    
    if not has_access:
        return jsonify({"error": "Conversation not found or access denied"}), 404
    
    # Generate title using AI
    title = generate_conversation_title(conversation_id)
    
    if title:
        # Store the generated title as custom title
        global _custom_titles
        _custom_titles[conversation_id] = title
        
        # Save to file
        save_conversation_memory_with_titles(conversation_memory, _custom_titles)
        
        return jsonify({"success": True, "title": title})
    else:
        return jsonify({"error": "Could not generate title"}), 500

# Delete conversation
@app.route('/delete_conversation', methods=['POST'])
def delete_conversation():
    data = request.json
    conversation_id = data.get('conversation_id', '')
    user_id = get_user_id_from_session()
    
    if not conversation_id:
        return jsonify({"error": "Missing conversation_id"}), 400
    
    # Security: Check if user has access to delete this conversation
    has_access = False
    
    if user_id == 'anonymous':
        # Anonymous users can only delete conversations in their session
        session_id = session.get('session_id')
        if conversation_id == session_id and conversation_id in conversation_memory:
            has_access = True
    else:
        # Authenticated users can delete their own conversations
        if conversation_id.startswith(f"conv_{user_id}_") and conversation_id in conversation_memory:
            has_access = True
        
        # Also check local user conversations file
        if not has_access:
            user_conversations = load_user_conversations_locally(user_id)
            if conversation_id in user_conversations:
                has_access = True
        
        # Also check Firebase for user's conversations
        if not has_access and firebase_initialized:
            firebase_conversations = get_conversations_from_firebase(user_id)
            if conversation_id in firebase_conversations:
                has_access = True
    
    if not has_access:
        return jsonify({"error": "Conversation not found or access denied"}), 404
    
    # === FIREBASE FIRST APPROACH ===
    if user_id != 'anonymous' and firebase_initialized:
        # Delete from Firebase first
        success = delete_conversation_from_firebase(user_id, conversation_id)
        if success:
            print(f"🔥 Conversation deleted from Firebase: {conversation_id}")
            
            # Also remove from local memory cache
            if conversation_id in conversation_memory:
                del conversation_memory[conversation_id]
            
            return jsonify({"success": True})
    
    # === FALLBACK TO LOCAL STORAGE ===
    # Remove conversation from local memory
    if conversation_id in conversation_memory:
        del conversation_memory[conversation_id]
        print(f"💾 Conversation deleted from local memory: {conversation_id}")
    
    # Also remove from user's local conversation file
    user_conversations = load_user_conversations_locally(user_id)
    if conversation_id in user_conversations:
        del user_conversations[conversation_id]
        # Save updated user conversations by overwriting the entire file
        import os
        user_file_path = f"data/users/{user_id}/conversations.json"
        os.makedirs(os.path.dirname(user_file_path), exist_ok=True)
        with open(user_file_path, 'w', encoding='utf-8') as f:
            json.dump(user_conversations, f, ensure_ascii=False, indent=2)
        print(f"📁 Conversation deleted from user's local file: {conversation_id}")
    
    # Remove custom title if exists
    global _custom_titles
    if conversation_id in _custom_titles:
        del _custom_titles[conversation_id]
        print(f"🏷️ Custom title deleted from local storage: {conversation_id}")
    
    # Save updated memory
    save_conversation_memory_with_titles(conversation_memory, _custom_titles)
    
    return jsonify({"success": True})

# Get Firebase status - New Route
@app.route('/firebase_status', methods=['GET'])
def get_firebase_status():
    """
    Get Firebase connection status
    احصل على حالة اتصال Firebase
    """
    return jsonify({
        "firebase_initialized": firebase_initialized,
        "firebase_available": firebase_initialized,
        "message": "Firebase متاح" if firebase_initialized else "Firebase غير متاح"
    })

# File upload endpoint
@app.route('/upload_file', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        # Check if the user is authenticated
        user_id = get_user_id_from_session()
        conversation_id = request.form.get('conversation_id', '')
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Define allowed extensions
        ALLOWED_EXTENSIONS = {
            'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
            'files': {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'zip'}
        }
        
        # Function to check if file extension is allowed
        def allowed_file(filename, file_type='files'):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())
        
        # Function to get file type based on extension
        def get_file_type(filename):
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            if ext in ALLOWED_EXTENSIONS['images']:
                return 'images'
            return 'files'
        
        if file and (allowed_file(file.filename, 'images') or allowed_file(file.filename, 'files')):
            # Secure the filename to prevent directory traversal attacks
            filename = secure_filename(file.filename)
            
            # Add unique identifier to prevent filename collisions
            file_id = str(uuid.uuid4())[:8]
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{file_id}{ext}"
            
            # Determine file type and save to appropriate folder
            file_type = get_file_type(filename)
            
            # Create upload directories if they don't exist
            upload_folder = 'uploads'
            os.makedirs(os.path.join(upload_folder, 'images'), exist_ok=True)
            os.makedirs(os.path.join(upload_folder, 'files'), exist_ok=True)
            
            file_path = os.path.join(upload_folder, file_type, unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Get file metadata
            file_size = os.path.getsize(file_path)
            file_url = f"/uploads/{file_type}/{unique_filename}"
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Create file metadata
            file_data = {
                'filename': filename,
                'unique_filename': unique_filename,
                'file_type': file_type,
                'mime_type': mime_type,
                'file_size': file_size,
                'file_url': file_url,
                'upload_time': time.time(),
                'user_id': user_id,
                'conversation_id': conversation_id
            }
            
            # Record file upload in conversation
            if conversation_id:
                # Create a message about the file upload
                if file_type == 'images':
                    message = f"[تم رفع صورة | Image uploaded: {filename}]"
                    
                    # Generate a more helpful response for images
                    bot_response = "تم استلام الصورة. يمكنك الآن أن تسألني عن محتوى الصورة وسأحاول تحليلها.\n\nImage received. You can now ask me about the content of the image and I'll try to analyze it."
                else:
                    # For other files, add a generic response
                    message = f"[تم رفع ملف | File uploaded: {filename}]"
                    bot_response = f"تم استلام الملف {filename}. ما الذي تريد أن أفعله بهذا الملف؟\n\nFile {filename} received. What would you like me to do with this file?"
                
                # Record the messages
                record_message(conversation_id, "user", message, file_data=file_data)
                record_message(conversation_id, "assistant", bot_response)
            
            return jsonify({
                'success': True,
                'file_data': file_data,
                'message': 'File uploaded successfully',
                'bot_response': bot_response if conversation_id else None
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        print(f"Error in file upload: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<file_type>/<filename>')
def uploaded_file(file_type, filename):
    """Serve uploaded files"""
    if file_type not in ['images', 'files']:
        return "Invalid file type", 400
    
    return send_from_directory(os.path.join('uploads', file_type), filename)

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    """Analyze an uploaded image using Gemini"""
    try:
        data = request.json
        image_url = data.get('image_url')
        question = data.get('question')
        conversation_id = data.get('conversation_id', '')
        
        if not image_url or not question:
            return jsonify({'error': 'Missing image_url or question'}), 400
        
        # Get the full path to the image
        image_path = os.path.join(os.getcwd(), image_url.lstrip('/'))
        
        if not os.path.exists(image_path):
            return jsonify({'error': f'Image not found at path: {image_path}'}), 404
        
        # Use Gemini to analyze the image
        if genai_available:
            try:
                # Configure Gemini API
                genai.configure(api_key=config.GEMINI_API_KEY)
                
                # Create a multimodal model
                vision_model = genai.GenerativeModel('gemini-pro-vision')
                
                # Load the image
                image_parts = [
                    {
                        "mime_type": "image/jpeg",  # Adjust based on actual image type
                        "data": open(image_path, "rb").read()
                    }
                ]
                
                # Create the prompt with the question
                prompt = f"""أنا أرسلت لك صورة. {question}

I sent you an image. {question}

Please analyze the image and provide a detailed response in both Arabic and English."""
                
                # Generate the response
                response = vision_model.generate_content([prompt, image_parts[0]])
                
                if response and response.text:
                    analysis = response.text.strip()
                    
                    # Record the question and answer in the conversation with enhanced features
                    if conversation_id:
                        # Create file data for the image
                        file_data = {
                            "filename": os.path.basename(image_path),
                            "file_type": "images",
                            "file_url": image_url
                        }
                        record_enhanced_message(conversation_id, "user", question, file_data)
                        record_enhanced_message(conversation_id, "assistant", analysis)
                    
                    return jsonify({
                        'success': True,
                        'analysis': analysis
                    })
                else:
                    return jsonify({'error': 'Failed to analyze image'}), 500
                
            except Exception as e:
                print(f"Error analyzing image with Gemini: {e}")
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500
        else:
            fallback_response = """
            لم أتمكن من تحليل الصورة لأن واجهة برمجة التطبيقات للرؤية غير متاحة. يمكنك وصف ما تراه في الصورة وسأحاول مساعدتك.
            
            I couldn't analyze the image because the vision API is not available. You can describe what you see in the image and I'll try to help you.
            """
            
            # Record the fallback response
            if conversation_id:
                record_message(conversation_id, "assistant", fallback_response)
                
            return jsonify({
                'success': True,
                'analysis': fallback_response,
                'is_fallback': True
            })
            
    except Exception as e:
        print(f"Error in analyze_image: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Add streaming response endpoint
@app.route('/stream_message', methods=['POST'])
def stream_message():
    """Stream long responses in chunks to prevent browser crashes"""
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        conversation_id = data.get('conversation_id', '')
        
        if not user_input:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get response from Gemini
        response_text = get_gemini_response(user_input, conversation_id)
        
        if not response_text:
            return jsonify({'error': 'Failed to generate response'}), 500
        
        # Check if response is too long
        if len(response_text) > config.MAX_RESPONSE_LENGTH:
            # Truncate response and add warning
            response_text = response_text[:config.MAX_RESPONSE_LENGTH] + "\n\n⚠️ **تم اختصار الاستجابة لمنع توقف المتصفح | Response truncated to prevent browser crash**"
        
        # Record the full conversation
        record_message(conversation_id, "user", user_input)
        record_message(conversation_id, "assistant", response_text)
        
        # Return response with streaming flag
        return jsonify({
            'success': True,
            'response': response_text,
            'streaming': len(response_text) > 1000,  # Enable streaming for long responses
            'chunks': split_response_into_chunks(response_text) if len(response_text) > 1000 else [response_text]
        })
        
    except Exception as e:
        print(f"Error in stream_message: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def split_response_into_chunks(text, chunk_size=None):
    """Split long text into manageable chunks"""
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE
    
    # Split by sentences first to maintain readability
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed chunk size, start a new chunk
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
        else:
            current_chunk += sentence + ". "
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

# Modify the existing get_gemini_response function to handle timeouts
def get_gemini_response(user_input, session_id, language="english"):
    """
    Get response from Gemini API with enhanced context and safety
    الحصول على استجابة من API Gemini مع سياق محسن وأمان
    """
    
    if not gemini_available:
        return None
    
    try:
        def timeout_handler(signum, frame):
            raise TimeoutError("Gemini API call timed out")
        
        # Set timeout alarm (Linux/Mac only - Windows doesn't support signals)
        import platform
        if platform.system() != "Windows":
            import signal
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(config.RESPONSE_TIMEOUT)
        
        # Get conversation context with enhanced understanding
        context = get_enhanced_conversation_context(session_id)
        
        # Get user profile for personalization
        user_id = get_user_id_from_session()
        user_profile = get_user_long_term_memory(user_id)
        
        # Build comprehensive prompt
        prompt = build_context_aware_prompt(user_input, context, user_profile, language)
        
        # Add specific anti-markdown instructions
        additional_instructions = """

CRITICAL: Output format instructions:
- Return ONLY plain text
- No markdown formatting symbols (**, *, `, _, #, etc.)
- No HTML tags
- No special characters for formatting
- Write code on separate lines with simple indentation
- Use simple dashes for lists: - item
- Keep all text as plain, readable text

إرشادات التنسيق الحرجة:
- أرجع نص عادي فقط
- لا رموز تنسيق markdown (**, *, `, _, #, إلخ)
- لا علامات HTML
- لا أحرف خاصة للتنسيق  
- اكتب الكود في أسطر منفصلة مع مسافات بسيطة
- استخدم شرطات بسيطة للقوائم: - عنصر
- اجعل كل النص عادي وقابل للقراءة
"""
        
        full_prompt = prompt + additional_instructions
        
        # Generate response
        response = gemini_model.generate_content(full_prompt)
        
        # Clear timeout alarm
        if platform.system() != "Windows":
            signal.alarm(0)
        
        if response and response.text:
            response_text = response.text.strip()
            
            # Clean response from any remaining markdown symbols
            response_text = clean_markdown_symbols(response_text)
            
            return response_text
        else:
            return None
            
    except Exception as e:
        # Clear timeout alarm in case of error
        if platform.system() != "Windows":
            try:
                signal.alarm(0)
            except:
                pass
        
        print(f"Gemini API error: {e}")
        traceback.print_exc()
        return None

def clean_markdown_symbols(text):
    """
    Remove markdown formatting symbols to prevent browser hanging
    إزالة رموز تنسيق markdown لمنع تجميد المتصفح
    """
    import re
    
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', ''), text)
    
    # Remove inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove bold and italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    return text

if __name__ == '__main__':
    # Try to run on port 80 first, then fallback to 5000 if permission denied
    import sys
    try:
        print("Starting AI Chatbot on port 80 (HTTP default)...")
        # Run Flask with explicit settings for global accessibility on HTTP default port
        app.run(host="0.0.0.0", port=80, debug=True)
    except PermissionError:
        print("\n⚠️  Permission denied for port 80. Requires Administrator privileges.")
        print("🔄 Falling back to port 5000...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except OSError as e:
        if "10013" in str(e) or "Permission denied" in str(e):
            print("\n⚠️  Port 80 is already in use or requires Administrator privileges.")
            print("🔄 Falling back to port 5000...")
            app.run(host="0.0.0.0", port=5000, debug=True)
        else:
            print(f"❌ Error starting server: {e}")
            sys.exit(1) 