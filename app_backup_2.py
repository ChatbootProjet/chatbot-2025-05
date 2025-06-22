from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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

# Memory file paths
CONVERSATION_MEMORY_FILE = 'data/conversation_memory.json'
LEARNING_MEMORY_FILE = 'data/learning_memory.json'

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Initialize conversation memory
def init_conversation_memory():
    if os.path.exists(CONVERSATION_MEMORY_FILE):
        with open(CONVERSATION_MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

# Initialize learning memory
def init_learning_memory():
    if os.path.exists(LEARNING_MEMORY_FILE):
        with open(LEARNING_MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "pattern_frequency": {},
            "user_corrections": {},
            "similar_queries": defaultdict(list)
        }

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

# Parse and sanitize markdown
def parse_markdown(text):
    if not config.ENABLE_MARKDOWN:
        return text
    
    # Convert markdown to HTML
    html = markdown2.markdown(text, extras=config.MARKDOWN_EXTENSIONS)
    
    # Sanitize HTML for security
    clean_html = bleach.clean(
        html,
        tags=config.ALLOWED_MARKDOWN_TAGS,
        attributes={'a': ['href', 'title', 'target']},
        strip=True
    )
    
    return clean_html

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

# Load memories
conversation_memory = init_conversation_memory_with_titles()
learning_memory = init_learning_memory()
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
    "bot": [
        "I'm just a simple chatbot created with Python! I can learn from our conversations and leverage Gemini AI to provide more advanced responses.",
        "I'm a chatbot built with Python. I'm designed to improve over time by learning from interactions and by using Gemini AI for complex questions.",
        "أنا مجرد روبوت محادثة بسيط تم إنشاؤه باستخدام Python! يمكنني التعلم من محادثاتنا واستخدام Gemini AI لتقديم ردود أكثر تقدمًا.",
        "أنا روبوت محادثة تم بناؤه بدون استخدام Python. تم تصميمي للتحسن مع مرور الوقت من خلال التعلم من التفاعلات واستخدام Gemini AI للأسئلة المعقدة."
    ],
    "capabilities": [
        "I can chat with you in English and Arabic. I can answer simple questions, have basic conversations, and use Gemini AI for more complex questions. I'm also able to learn from our interactions!",
        "I'm a bilingual chatbot that can understand both English and Arabic. I have a basic understanding of conversation flow, I can use Gemini AI for advanced responses, and I learn from our chats.",
        "يمكنني التحدث معك باللغتين الإنجليزية والعربية. يمكنني الإجابة على الأسئلة البسيطة وإجراء محادثات أساسية واستخدام Gemini AI للأسئلة الأكثر تعقيدًا. كما يمكنني التعلم من تفاعلاتنا!",
        "أنا روبوت محادثة ثنائي اللغة يمكنه فهم كل من اللغة الإنجليزية والعربية. لدي فهم أساسي لتدفق المحادثة، ويمكنني استخدام Gemini AI للردود المتقدمة، وأتعلم من محادثاتنا."
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
        "I can chat with you in English or Arabic. You can ask me about myself, the time, date, or just have a casual conversation! If I make a mistake, you can teach me by saying 'Learn: [correct response]'",
        "يمكنني التحدث معك باللغة الإنجليزية أو العربية. يمكنك أن تسألني عن نفسي، الوقت، التاريخ، أو مجرد إجراء محادثة عادية! إذا ارتكبت خطأ، يمكنك تعليمي بقول 'تعلم: [الرد الصحيح]'"
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
        "Using advanced AI to answer...",
        "استخدام الذكاء الاصطناعي المتقدم للإجابة..."
    ],
    "markdown": [
        "I support Markdown formatting! You can use **bold**, *italic*, `code`, lists, and more in your messages.",
        "أنا أدعم تنسيق Markdown! يمكنك استخدام **غامق**، *مائل*، `الكود`، والقوائم، والمزيد في رسائلك."
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
    "markdown": r"(markdown|formatting|تنسيق|ماركداون)"
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

# Get conversation context
def get_conversation_context(session_id, limit=None):
    """
    Get conversation context for the AI
    الحصول على سياق المحادثة للذكاء الاصطناعي
    """
    if session_id not in conversation_memory:
        return []
    
    messages = conversation_memory[session_id]
    if limit:
        messages = messages[-limit:]
    
    # Format messages for Gemini API
    formatted_messages = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        formatted_messages.append({
            "role": role,
            "parts": [msg["message"]]
        })
    
    return formatted_messages

# Detect if user is asking for code
def detect_code_request(user_input):
    """
    Detect if the user is asking for code
    اكتشاف ما إذا كان المستخدم يطلب كوداً
    """
    code_keywords_en = ["code", "program", "script", "function", "class", "algorithm", "implementation", "syntax"]
    code_keywords_ar = ["كود", "برنامج", "سكريبت", "دالة", "كلاس", "خوارزمية", "تنفيذ", "صيغة"]
    
    user_input_lower = user_input.lower()
    
    # Check English keywords
    for keyword in code_keywords_en:
        if keyword in user_input_lower:
            return True
    
    # Check Arabic keywords
    for keyword in code_keywords_ar:
        if keyword in user_input_lower:
            return True
    
    return False

def enhance_code_response(response_text, user_input):
    """
    Return clean response without modifications for natural Markdown rendering
    إرجاع الاستجابة نظيفة بدون تعديلات لعرض Markdown الطبيعي
    """
    # Just return the original response - let Markdown work naturally
    return response_text

def get_gemini_response(user_input, session_id, language="english"):
    if not gemini_available:
        return None
    
    try:
        # Get conversation context
        context = get_conversation_context(session_id)
        
        # Check if this is a code-related request
        is_code_request = detect_code_request(user_input)
        
        # Create a chat session with context if available
        if context and config.PRESERVE_CONVERSATION_HISTORY:
            chat = gemini_model.start_chat(history=context)
            response = chat.send_message(user_input)
        else:
            # Enhanced prompts for code requests
            if is_code_request:
                if language == "arabic":
                    system_prompt = """
                    أنت مساعد برمجة خبير. عند تقديم الكود:
                    
                    1. اشرح المشكلة أو المفهوم بوضوح
                    2. قدم الكود داخل كتل Markdown نظيفة باستخدام ```language
                    3. أضف تعليقات مفيدة داخل الكود
                    4. اشرح أجزاء الكود المهمة بعد عرضه
                    
                    **مهم جداً**: استخدم تنسيق Markdown الطبيعي فقط:
                    - ```javascript للكود
                    - **النص الغامق** للعناوين المهمة
                    - القوائم العادية للخطوات
                    - لا تضع HTML أو تنسيقات معقدة
                    
                    اجعل الكود نظيفاً وواضحاً مع تعليقات باللغة العربية داخل الكود.
                    """
                else:
                    system_prompt = """
                    You are an expert programming assistant. When providing code:
                    
                    1. Explain the problem or concept clearly
                    2. Provide code in clean Markdown blocks using ```language
                    3. Add helpful comments inside the code
                    4. Explain important parts of the code after showing it
                    
                    **Very Important**: Use natural Markdown formatting only:
                    - ```javascript for code blocks
                    - **bold text** for important headings
                    - Regular lists for steps
                    - No HTML or complex formatting
                    
                    Keep the code clean and clear with helpful comments.
                    """
            
            if language == "arabic":
                prompt = f"{system_prompt}\n\nالسؤال: {user_input}\n\nالإجابة:"
            else:
                prompt = f"{system_prompt}\n\nQuestion: {user_input}\n\nResponse:"
            
            response = gemini_model.generate_content(prompt)
        
        if response and response.text:
            # Clean the response text
            cleaned_response = response.text.strip()
            
            # Remove any "Question:" or "Response:" or "الإجابة:" prefixes that might be in the response
            cleaned_response = re.sub(r'^(Question:|Response:|الإجابة:|الجواب:)\s*', '', cleaned_response, flags=re.IGNORECASE)
            
            # Enhance code responses with literate programming format
            if is_code_request:
                cleaned_response = enhance_code_response(cleaned_response, user_input)
            
            # Return the full response without length limitation
            return cleaned_response
        
        return None
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        traceback.print_exc()
        return None

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
def record_message(session_id, role, message):
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
    record_message(session_id, "user", user_input)
    
    # Preprocess input
    preprocessed_input = preprocess_text(user_input)
    
    # Check for learned responses
    learned_response = find_similar_question(preprocessed_input)
    if learned_response:
        record_message(session_id, "bot", learned_response)
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
    
    # Detect language
    language = detect_language(user_input)
    
    # Check for markdown inquiry
    if re.search(patterns["markdown"], preprocessed_input, re.IGNORECASE):
        if language == 'arabic':
            markdown_response = responses["markdown"][1]
        else:
            markdown_response = responses["markdown"][0]
        record_message(session_id, "bot", markdown_response)
        return markdown_response
    
    # If we're configured to use Gemini first, try that before pattern matching
    if config.USE_GEMINI_AFTER_ATTEMPTS == 0 and gemini_available:
        gemini_response = get_gemini_response(user_input, session_id, language)
        if gemini_response:
            record_message(session_id, "bot", gemini_response)
            return gemini_response
    
    # Check for simple patterns that don't need Gemini
    for intent in ["greeting", "farewell", "thanks", "time", "date"]:
        pattern = patterns.get(intent)
        if pattern and re.search(pattern, preprocessed_input, re.IGNORECASE):
            # Update pattern frequency for learning
            update_pattern_frequency(intent)
            
            # Get appropriate language response
            if language == 'arabic':
                # Choose Arabic responses (which are in odd positions: 2, 3)
                filtered_responses = [r for i, r in enumerate(responses[intent]) if i >= 2]
                if filtered_responses:
                    selected_response = random.choice(filtered_responses)
                    record_message(session_id, "bot", selected_response)
                    return selected_response
            else:
                # Choose English responses (which are in even positions: 0, 1)
                filtered_responses = [r for i, r in enumerate(responses[intent]) if i < 2]
                if filtered_responses:
                    selected_response = random.choice(filtered_responses)
                    record_message(session_id, "bot", selected_response)
                    return selected_response
    
    # For all other queries, use Gemini if available
    if gemini_available:
        gemini_response = get_gemini_response(user_input, session_id, language)
        if gemini_response:
            record_message(session_id, "bot", gemini_response)
            return gemini_response
    
    # If all else fails, return unknown response
    if language == 'arabic':
        unknown_response = random.choice(responses["unknown"][2:])
    else:
        unknown_response = random.choice(responses["unknown"][:2])
    
    record_message(session_id, "bot", unknown_response)
    return unknown_response

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
    user_message = request.json.get('message', '')
    conversation_id = request.json.get('conversation_id', '')
    is_regenerate = request.json.get('regenerate', False)
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get or create session ID
    session_id = session.get('session_id', str(time.time()))
    if 'session_id' not in session:
        session['session_id'] = session_id
    
    # Use conversation_id if provided, otherwise use session_id
    active_conversation_id = conversation_id if conversation_id else session_id
    
    # Add a small delay to simulate thinking
    time.sleep(config.THINKING_DELAY)
    
    # For regeneration, don't add the user message again to conversation history
    if not is_regenerate:
        # Record the user message
        record_message(active_conversation_id, 'user', user_message)
    
    # Get bot response
    bot_response = get_response(user_message, active_conversation_id)
    
    # Record the bot response
    record_message(active_conversation_id, 'assistant', bot_response)
    
    # Process markdown if enabled
    if config.ENABLE_MARKDOWN:
        bot_response_html = parse_markdown(bot_response)
    else:
        bot_response_html = bot_response
    
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
        'has_markdown': config.ENABLE_MARKDOWN and bot_response != bot_response_html,
        'conversation_id': active_conversation_id
    })

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

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG) 