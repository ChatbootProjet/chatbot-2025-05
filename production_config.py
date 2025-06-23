"""
Production Configuration for AI Chatbot Service
This file contains optimized settings for running the chatbot as a Windows service.
"""
import os

# Server settings - Production optimized
HOST = '0.0.0.0'  # Listen on all interfaces for network access
PORT = 5000  # Standard port for Flask applications
DEBUG = False  # Disable debug mode for production

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-super-secret-production-key-change-this')

# Performance settings
THINKING_DELAY = 0.1  # Reduced delay for faster responses
MAX_MESSAGE_LENGTH = 8000  # Increased for better user experience
CONTEXT_MESSAGES = 15  # Balanced context for performance
MAX_RESPONSE_LENGTH = 6000  # Prevent extremely long responses

# Gemini API settings - Production optimized
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', "AIzaSyDemWygf7TEHJcGRiyfeag4GOmE4UEdMbM")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_VISION_MODEL = "gemini-pro-vision"
USE_GEMINI_AFTER_ATTEMPTS = 0  # Always use Gemini for consistent responses
GEMINI_TEMPERATURE = 0.6  # Slightly reduced for more consistent responses
GEMINI_MAX_OUTPUT_TOKENS = 3072  # Optimized for performance
GEMINI_TOP_P = 0.9  # Balanced creativity and consistency
GEMINI_TOP_K = 30  # Focused responses

# File upload settings
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB for production
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
ALLOWED_FILE_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'zip', 'rar'}

# Logging settings
ENABLE_LOGGING = True
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/chatbot.log'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Firebase settings - Production
FIREBASE_CONFIG = {
    "apiKey": os.environ.get('FIREBASE_API_KEY', "AIzaSyAsNKxsrz6J6gLJ2yFrRUGwAq_RHCvf9ks"),
    "authDomain": "chat-bot-ee488.firebaseapp.com",
    "databaseURL": "https://chat-bot-ee488-default-rtdb.firebaseio.com",
    "projectId": "chat-bot-ee488",
    "storageBucket": "chat-bot-ee488.firebasestorage.app",
    "messagingSenderId": "261952313842",
    "appId": "1:261952313842:web:95cc49e11c99b58d8bf36b8bf36b"
}

USE_FIREBASE_STORAGE = True
FIREBASE_SERVICE_ACCOUNT = os.environ.get('FIREBASE_SERVICE_ACCOUNT', "firebase-service-account.json")

# Response settings - Production optimized
ENABLE_STREAMING = True
RESPONSE_TIMEOUT = 45  # Increased timeout for complex queries
CHUNK_SIZE = 150  # Optimized chunk size for streaming
ENABLE_MARKDOWN = True

# Cache settings
ENABLE_RESPONSE_CACHE = True
CACHE_TIMEOUT = 300  # 5 minutes cache for similar queries
MAX_CACHE_SIZE = 1000  # Maximum cached responses

# Rate limiting
ENABLE_RATE_LIMITING = True
RATE_LIMIT_PER_MINUTE = 60  # Requests per minute per IP
RATE_LIMIT_PER_HOUR = 1000  # Requests per hour per IP

# Language settings
DEFAULT_LANGUAGE = 'arabic'  # Default to Arabic for better user experience
SUPPORTED_LANGUAGES = ['english', 'arabic', 'french', 'spanish']

# UI settings
DEFAULT_GREETING = """
مرحباً بك في خدمة الذكاء الاصطناعي!
كيف يمكنني مساعدتك اليوم؟

Welcome to AI Assistant Service!
How can I help you today?
"""

# Health check settings
ENABLE_HEALTH_CHECK = True
HEALTH_CHECK_ENDPOINT = '/health'

# Monitoring settings
ENABLE_METRICS = True
METRICS_ENDPOINT = '/metrics'

# Backup settings
AUTO_BACKUP = True
BACKUP_INTERVAL = 3600  # 1 hour in seconds
BACKUP_RETENTION_DAYS = 30
BACKUP_DIRECTORY = 'backups'

# Environment detection
ENVIRONMENT = 'production'
SERVICE_NAME = 'AIChatbotService'
SERVICE_DESCRIPTION = 'AI Chatbot Service with Flask and Gemini API' 