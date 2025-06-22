"""
Configuration file for the Chatbot application
This file contains settings that can be adjusted to customize your chatbot's behavior.
"""
import os

# Server settings
HOST = '0.0.0.0'  # Use '0.0.0.0' to make the server publicly accessible, '127.0.0.1' for local only
PORT = 5000  # The port number to run the server on
DEBUG = True  # Set to False in production

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
GEMINI_API_KEY = "AIzaSyDemWygf7TEHJcGRiyfeag4GOmE4UEdMbM"  # API key for Gemini
GEMINI_MODEL = "gemini-2.0-flash"  # Model to use
GEMINI_VISION_MODEL = "gemini-pro-vision"  # Vision model for image analysis
USE_GEMINI_AFTER_ATTEMPTS = 0.1  # Use Gemini as primary response engine (0 = always use Gemini first)
GEMINI_TEMPERATURE = 0.7  # Controls randomness (0.0 to 1.0) - balanced for coherent long responses
GEMINI_MAX_OUTPUT_TOKENS = 4096  # Maximum length of generated responses (reduced to prevent browser crashes)
GEMINI_TOP_P = 0.95  # Top probability mass of tokens to consider
GEMINI_TOP_K = 40  # Number of highest probability tokens to consider (reduced for more focused responses)

# File upload settings
UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded files
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maximum file size (16MB)
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}  # Allowed image file extensions
ALLOWED_FILE_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'zip'}  # Allowed document file extensions

# Conversation context settings
CONTEXT_MESSAGES = 20  # Number of previous messages to include for context (reduced for better performance)
PRESERVE_CONVERSATION_HISTORY = True  # Whether to keep conversation history for context 

# Markdown settings
ENABLE_MARKDOWN = True  # Enable Markdown parsing and rendering
ALLOWED_MARKDOWN_TAGS = [    # HTML tags allowed in markdown output for security
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'ul', 'ol', 
    'li', 'code', 'pre', 'blockquote', 'a', 'br', 'hr'
]
MARKDOWN_EXTENSIONS = [      # Extensions for the markdown parser
    'extra', 'codehilite', 'tables', 'smarty'
]

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
MAX_RESPONSE_LENGTH = 8000  # Maximum response length to prevent browser crashes 