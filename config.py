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
MAX_MESSAGE_LENGTH = 1000  # Maximum length of user messages to process

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
USE_GEMINI_AFTER_ATTEMPTS = 0  # Use Gemini as primary response engine (0 = always use Gemini first)
GEMINI_TEMPERATURE = 0.7  # Controls randomness (0.0 to 1.0) - higher is more human-like
GEMINI_MAX_OUTPUT_TOKENS = 300  # Maximum length of generated responses
GEMINI_TOP_P = 0.95  # Top probability mass of tokens to consider
GEMINI_TOP_K = 40  # Number of highest probability tokens to consider

# Conversation context settings
CONTEXT_MESSAGES = 5  # Number of previous messages to include for context
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