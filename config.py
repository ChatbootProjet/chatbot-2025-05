"""
Configuration file for the Chatbot application
This file contains settings that can be adjusted to customize your chatbot's behavior.
"""
import os

# Server settings
HOST = '0.0.0.0'  # Use '0.0.0.0' to make the server publicly accessible, '127.0.0.1' for local only
PORT = 80  # HTTP default port for web access without specifying port number
DEBUG = os.environ.get('FLASK_ENV') != 'production'  # Auto-detect production mode

# Chatbot behavior settings
THINKING_DELAY = 0.5  # Delay in seconds to simulate "thinking" before responding
MAX_MESSAGE_LENGTH = 5000  # Maximum length of user messages to process (increased for long code/text)

# Language settings
DEFAULT_LANGUAGE = 'english'  # Default language if detection fails
SUPPORTED_LANGUAGES = ['english', 'arabic']

# UI settings
DEFAULT_GREETING = """
مرحباً! كيف يمكنني مساعدتك اليوم؟ 
Hello! How can I help you today?
"""

# Gemini API settings
GEMINI_API_KEY = "AIzaSyC6cap85BFDabn1E2zqyctk6Qw4fOkHFhw"  # Disabled temporarily due to quota exceeded
GEMINI_MODEL = "gemini-2.0-flash"  # Model to use
GEMINI_VISION_MODEL = "gemini-pro-vision"  # Vision model for image analysis
USE_GEMINI_AFTER_ATTEMPTS = 999  # Use local responses first (disabled Gemini)
GEMINI_TEMPERATURE = 0.7  # Controls randomness (0.0 to 1.0) - balanced for coherent long responses
GEMINI_MAX_OUTPUT_TOKENS = 2048  # Reduced to prevent browser crashes (was 4096)
GEMINI_TOP_P = 0.95  # Top probability mass of tokens to consider
GEMINI_TOP_K = 40  # Number of highest probability tokens to consider (reduced for more focused responses)

# File upload settings
UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded files
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maximum file size (16MB)
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}  # Allowed image file extensions
ALLOWED_FILE_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'zip'}  # Allowed document file extensions

# Enhanced conversation context settings
CONTEXT_MESSAGES = 30  # Number of previous messages to include for context (increased for better memory)
PRESERVE_CONVERSATION_HISTORY = True  # Whether to keep conversation history for context
LONG_TERM_MEMORY_ENABLED = True  # Enable long-term user memory and personalization
SEMANTIC_CONTEXT_ANALYSIS = True  # Enable semantic analysis of conversations for better context understanding 

# Markdown settings - DISABLED TO PREVENT BROWSER HANGING
ENABLE_MARKDOWN = False  # CRITICAL: Keep disabled to prevent browser crashes on large code blocks
PROCESS_MARKDOWN = False  # Additional flag to ensure no markdown processing
ALLOWED_MARKDOWN_TAGS = []  # Empty list - no HTML tags allowed for security
MARKDOWN_EXTENSIONS = []  # Empty list - no markdown extensions

# Response formatting settings  
FORCE_PLAIN_TEXT = True  # Force all responses to be plain text only
STRIP_FORMATTING_SYMBOLS = True  # Remove any formatting symbols from responses
MAX_CODE_BLOCK_SIZE = 2000  # Maximum characters in code responses to prevent hanging

# Firebase settings
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAsNKxsrz6J6gLJ2yFrRUGwAq_RHCvf9ks",
    "authDomain": "chat-bot-ee488.firebaseapp.com",
    "databaseURL": "https://chat-bot-ee488-default-rtdb.firebaseio.com",
    "projectId": "chat-bot-ee488",
    "storageBucket": "chat-bot-ee488.firebasestorage.app",
    "messagingSenderId": "261952313842",
    "appId": "1:261952313842:web:95cc49e11c99b58d8bf36b"
}

# Firebase Admin settings
USE_FIREBASE_STORAGE = True  # Enable Firebase for storing conversations and learning data
FIREBASE_SERVICE_ACCOUNT = "firebase-service-account.json"  # Path to service account key file 

# Response streaming and timeout settings
ENABLE_STREAMING = True  # Enable streaming responses for long content
RESPONSE_TIMEOUT = 30  # Maximum time (seconds) to wait for a response
CHUNK_SIZE = 100  # Number of characters to send in each chunk for streaming
MAX_RESPONSE_LENGTH = 4000  # Reduced to prevent browser crashes (was 8000) 