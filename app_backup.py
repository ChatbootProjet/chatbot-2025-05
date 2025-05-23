from flask import Flask, render_template, request, jsonify, session
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

app = Flask(__name__)
app.secret_key = 'chatbot_learning_secret_key'  # Secret key for session management

# Download NLTK data on first run
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Initialize Gemini models
gemini_models = {}
gemini_available = False

try:
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    # Initialize all available models
    for model_id in config.GEMINI_MODELS:
        try:
            gemini_models[model_id] = genai.GenerativeModel(
                model_name=model_id,
        generation_config={
            "temperature": config.GEMINI_TEMPERATURE,
            "max_output_tokens": config.GEMINI_MAX_OUTPUT_TOKENS,
            "top_p": config.GEMINI_TOP_P,
            "top_k": config.GEMINI_TOP_K
        }
    )
            print(f"Initialized Gemini model: {model_id}")
        except Exception as e:
            print(f"Error initializing Gemini model {model_id}: {e}")
            traceback.print_exc()
    
    # If at least one model is available, set gemini_available to True
    if gemini_models:
        gemini_available = True
        print("Gemini API initialized successfully with models:", ", ".join(gemini_models.keys()))
    else:
        print("No Gemini models were successfully initialized")
except Exception as e:
    print(f"Error initializing Gemini API: {e}")
    traceback.print_exc()

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

# Load memories
conversation_memory = init_conversation_memory()
learning_memory = init_learning_memory()
if isinstance(learning_memory["similar_queries"], dict):
    learning_memory["similar_queries"] = defaultdict(list, learning_memory["similar_queries"])

# Simple responses dictionary - both in English and Arabic
responses = {
    "greeting": [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Ù…Ø±Ø­Ø¨Ø§Ù‹! ÙƒÙŠÙ ÙŠÙ…ÙƒÙ†Ù†ÙŠ Ù…Ø³Ø§Ø¹Ø¯ØªÙƒ Ø§Ù„ÙŠÙˆÙ…ØŸ",
        "Ø£Ù‡Ù„Ø§Ù‹! Ù…Ø§Ø°Ø§ ÙŠÙ…ÙƒÙ†Ù†ÙŠ Ø£Ù† Ø£ÙØ¹Ù„ Ù„ÙƒØŸ"
    ],
    "farewell": [
        "Goodbye! Have a nice day!",
        "See you later!",
        "ÙˆØ¯Ø§Ø¹Ø§Ù‹! Ø£ØªÙ…Ù†Ù‰ Ù„Ùƒ ÙŠÙˆÙ…Ø§Ù‹ Ø³Ø¹ÙŠØ¯Ø§Ù‹!",
        "Ø¥Ù„Ù‰ Ø§Ù„Ù„Ù‚Ø§Ø¡!"
    ],
    "thanks": [
        "You're welcome!",
        "Happy to help!",
        "Ù„Ø§ Ø´ÙƒØ± Ø¹Ù„Ù‰ ÙˆØ§Ø¬Ø¨!",
        "Ø³Ø¹ÙŠØ¯ Ø¨Ø§Ù„Ù…Ø³Ø§Ø¹Ø¯Ø©!"
    ],
    "unknown": [
        "I'm not sure I understand. Can you rephrase that? If my response wasn't helpful, you can teach me by saying 'Learn: [correct response]'",
        "Hmm, I'm not sure about that. Can you try asking differently? You can teach me by saying 'Learn: [correct response]'",
        "Ù„Ø³Øª Ù…ØªØ£ÙƒØ¯Ø§Ù‹ Ù…Ù† ÙÙ‡Ù…ÙŠ. Ù‡Ù„ ÙŠÙ…ÙƒÙ†Ùƒ Ø¥Ø¹Ø§Ø¯Ø© ØµÙŠØ§ØºØ© Ø°Ù„ÙƒØŸ Ø¥Ø°Ø§ Ù„Ù… ØªÙƒÙ† Ø¥Ø¬Ø§Ø¨ØªÙŠ Ù…ÙÙŠØ¯Ø©ØŒ ÙŠÙ…ÙƒÙ†Ùƒ ØªØ¹Ù„ÙŠÙ…ÙŠ Ø¨Ù‚ÙˆÙ„ 'ØªØ¹Ù„Ù…: [Ø§Ù„Ø±Ø¯ Ø§Ù„ØµØ­ÙŠØ­]'",
        "Ù‡Ù…Ù…ØŒ Ù„Ø³Øª Ù…ØªØ£ÙƒØ¯Ø§Ù‹ Ù…Ù† Ø°Ù„Ùƒ. Ù‡Ù„ ÙŠÙ…ÙƒÙ†Ùƒ Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø© Ø¨Ø·Ø±ÙŠÙ‚Ø© Ù…Ø®ØªÙ„ÙØ©ØŸ ÙŠÙ…ÙƒÙ†Ùƒ ØªØ¹Ù„ÙŠÙ…ÙŠ Ø¨Ù‚ÙˆÙ„ 'ØªØ¹Ù„Ù…: [Ø§Ù„Ø±Ø¯ Ø§Ù„ØµØ­ÙŠØ­]'"
    ],
    "bot": [
        "I'm just a simple chatbot created with Python! I can learn from our conversations and leverage Gemini AI to provide more advanced responses.",
        "I'm a chatbot built with Python. I'm designed to improve over time by learning from interactions and by using Gemini AI for complex questions.",
        "Ø£Ù†Ø§ Ù…Ø¬Ø±Ø¯ Ø±ÙˆØ¨ÙˆØª Ù…Ø­Ø§Ø¯Ø«Ø© Ø¨Ø³ÙŠØ· ØªÙ… Ø¥Ù†Ø´Ø§Ø¤Ù‡ Ø¨Ø§Ø³ØªØ®Ø¯Ø§Ù… Python! ÙŠÙ…ÙƒÙ†Ù†ÙŠ Ø§Ù„ØªØ¹Ù„Ù… Ù…Ù† Ù…Ø­Ø§Ø¯Ø«Ø§ØªÙ†Ø§ ÙˆØ§Ø³ØªØ®Ø¯Ø§Ù… Gemini AI Ù„ØªÙ‚Ø¯ÙŠÙ… Ø±Ø¯ÙˆØ¯ Ø£ÙƒØ«Ø± ØªÙ‚Ø¯Ù…Ù‹Ø§.",
        "Ø£Ù†Ø§ Ø±ÙˆØ¨ÙˆØª Ù…Ø­Ø§Ø¯Ø«Ø© ØªÙ… Ø¨Ù†Ø§Ø¤Ù‡ Ø¨Ø¯ÙˆÙ† Ø§Ø³ØªØ®Ø¯Ø§Ù… Python. ØªÙ… ØªØµÙ…ÙŠÙ…ÙŠ Ù„Ù„ØªØ­Ø³Ù† Ù…Ø¹ Ù…Ø±ÙˆØ± Ø§Ù„ÙˆÙ‚Øª Ù…Ù† Ø®Ù„Ø§Ù„ Ø§Ù„ØªØ¹Ù„Ù… Ù…Ù† Ø§Ù„ØªÙØ§Ø¹Ù„Ø§Øª ÙˆØ§Ø³ØªØ®Ø¯Ø§Ù… Gemini AI Ù„Ù„Ø£Ø³Ø¦Ù„Ø© Ø§Ù„Ù…Ø¹Ù‚Ø¯Ø©."
    ],
    "capabilities": [
        "I can chat with you in English and Arabic. I can answer simple questions, have basic conversations, and use Gemini AI for more complex questions. I'm also able to learn from our interactions!",
        "I'm a bilingual chatbot that can understand both English and Arabic. I have a basic understanding of conversation flow, I can use Gemini AI for advanced responses, and I learn from our chats.",
        "ÙŠÙ…ÙƒÙ†Ù†ÙŠ Ø§Ù„ØªØ­Ø¯Ø« Ù…Ø¹Ùƒ Ø¨Ø§Ù„Ù„ØºØªÙŠÙ† Ø§Ù„Ø¥Ù†Ø¬Ù„ÙŠØ²ÙŠØ© ÙˆØ§Ù„Ø¹Ø±Ø¨ÙŠØ©. ÙŠÙ…ÙƒÙ†Ù†ÙŠ Ø§Ù„Ø¥Ø¬Ø§Ø¨Ø© Ø¹Ù„Ù‰ Ø§Ù„Ø£Ø³Ø¦Ù„Ø© Ø§Ù„Ø¨Ø³ÙŠØ·Ø© ÙˆØ¥Ø¬Ø±Ø§Ø¡ Ù…Ø­Ø§Ø¯Ø«Ø§Øª Ø£Ø³Ø§Ø³ÙŠØ© ÙˆØ§Ø³ØªØ®Ø¯Ø§Ù… Gemini AI Ù„Ù„Ø£Ø³Ø¦Ù„Ø© Ø§Ù„Ø£ÙƒØ«Ø± ØªØ¹Ù‚ÙŠØ¯Ù‹Ø§. ÙƒÙ…Ø§ ÙŠÙ…ÙƒÙ†Ù†ÙŠ Ø§Ù„ØªØ¹Ù„Ù… Ù…Ù† ØªÙØ§Ø¹Ù„Ø§ØªÙ†Ø§!",
        "Ø£Ù†Ø§ Ø±ÙˆØ¨ÙˆØª Ù…Ø­Ø§Ø¯Ø«Ø© Ø«Ù†Ø§Ø¦ÙŠ Ø§Ù„Ù„ØºØ© ÙŠÙ…ÙƒÙ†Ù‡ ÙÙ‡Ù… ÙƒÙ„ Ù…Ù† Ø§Ù„Ù„ØºØ© Ø§Ù„Ø¥Ù†Ø¬Ù„ÙŠØ²ÙŠØ© ÙˆØ§Ù„Ø¹Ø±Ø¨ÙŠØ©. Ù„Ø¯ÙŠ ÙÙ‡Ù… Ø£Ø³Ø§Ø³ÙŠ Ù„ØªØ¯ÙÙ‚ Ø§Ù„Ù…Ø­Ø§Ø¯Ø«Ø©ØŒ ÙˆÙŠÙ…ÙƒÙ†Ù†ÙŠ Ø§Ø³ØªØ®Ø¯Ø§Ù… Gemini AI Ù„Ù„Ø±Ø¯ÙˆØ¯ Ø§Ù„Ù…ØªÙ‚Ø¯Ù…Ø©ØŒ ÙˆØ£ØªØ¹Ù„Ù… Ù…Ù† Ù…Ø­Ø§Ø¯Ø«Ø§ØªÙ†Ø§."
    ],
    "weather": [
        "I'm sorry, I don't have access to real-time weather data. You would need to connect to a weather API for that feature.",
        "Ø£Ù†Ø§ Ø¢Ø³ÙØŒ Ù„ÙŠØ³ Ù„Ø¯ÙŠ ÙˆØµÙˆÙ„ Ø¥Ù„Ù‰ Ø¨ÙŠØ§Ù†Ø§Øª Ø§Ù„Ø·Ù‚Ø³ ÙÙŠ Ø§Ù„ÙˆÙ‚Øª Ø§Ù„ÙØ¹Ù„ÙŠ. Ø³ØªØ­ØªØ§Ø¬ Ø¥Ù„Ù‰ Ø§Ù„Ø§ØªØµØ§Ù„ Ø¨ÙˆØ§Ø¬Ù‡Ø© Ø¨Ø±Ù…Ø¬Ø© ØªØ·Ø¨ÙŠÙ‚Ø§Øª Ø§Ù„Ø·Ù‚Ø³ Ù„Ù‡Ø°Ù‡ Ø§Ù„Ù…ÙŠØ²Ø©."
    ],
    "time": [
        f"The current server time is {time.strftime('%H:%M:%S')}",
        f"Ø§Ù„ÙˆÙ‚Øª Ø§Ù„Ø­Ø§Ù„ÙŠ Ù„Ù„Ø®Ø§Ø¯Ù… Ù‡Ùˆ {time.strftime('%H:%M:%S')}"
    ],
    "date": [
        f"Today is {time.strftime('%Y-%m-%d')}",
        f"Ø§Ù„ÙŠÙˆÙ… Ù‡Ùˆ {time.strftime('%Y-%m-%d')}"
    ],
    "name": [
        "My name is ChatBot. What's yours?",
        "I'm ChatBot, your AI assistant.",
        "Ø§Ø³Ù…ÙŠ ChatBot. Ù…Ø§ Ù‡Ùˆ Ø§Ø³Ù…ÙƒØŸ",
        "Ø£Ù†Ø§ ChatBotØŒ Ù…Ø³Ø§Ø¹Ø¯Ùƒ Ø§Ù„Ø°ÙƒÙŠ."
    ],
    "help": [
        "I can chat with you in English or Arabic. You can ask me about myself, the time, date, or just have a casual conversation! If I make a mistake, you can teach me by saying 'Learn: [correct response]'",
        "ÙŠÙ…ÙƒÙ†Ù†ÙŠ Ø§Ù„ØªØ­Ø¯Ø« Ù…Ø¹Ùƒ Ø¨Ø§Ù„Ù„ØºØ© Ø§Ù„Ø¥Ù†Ø¬Ù„ÙŠØ²ÙŠØ© Ø£Ùˆ Ø§Ù„Ø¹Ø±Ø¨ÙŠØ©. ÙŠÙ…ÙƒÙ†Ùƒ Ø£Ù† ØªØ³Ø£Ù„Ù†ÙŠ Ø¹Ù† Ù†ÙØ³ÙŠØŒ Ø§Ù„ÙˆÙ‚ØªØŒ Ø§Ù„ØªØ§Ø±ÙŠØ®ØŒ Ø£Ùˆ Ù…Ø¬Ø±Ø¯ Ø¥Ø¬Ø±Ø§Ø¡ Ù…Ø­Ø§Ø¯Ø«Ø© Ø¹Ø§Ø¯ÙŠØ©! Ø¥Ø°Ø§ Ø§Ø±ØªÙƒØ¨Øª Ø®Ø·Ø£ØŒ ÙŠÙ…ÙƒÙ†Ùƒ ØªØ¹Ù„ÙŠÙ…ÙŠ Ø¨Ù‚ÙˆÙ„ 'ØªØ¹Ù„Ù…: [Ø§Ù„Ø±Ø¯ Ø§Ù„ØµØ­ÙŠØ­]'"
    ],
    "learning": [
        "I've learned this response. Thank you for teaching me!",
        "Got it! I'll remember this for next time.",
        "Ù„Ù‚Ø¯ ØªØ¹Ù„Ù…Øª Ù‡Ø°Ø§ Ø§Ù„Ø±Ø¯. Ø´ÙƒØ±Ø§Ù‹ Ù„ØªØ¹Ù„ÙŠÙ…ÙŠ!",
        "ÙÙ‡Ù…Øª! Ø³Ø£ØªØ°ÙƒØ± Ù‡Ø°Ø§ Ù„Ù„Ù…Ø±Ø© Ø§Ù„Ù‚Ø§Ø¯Ù…Ø©."
    ],
    "self_improvement": [
        "I'm designed to learn from our conversations. The more we chat, the better I get!",
        "Ø£Ù†Ø§ Ù…ØµÙ…Ù… Ù„Ù„ØªØ¹Ù„Ù… Ù…Ù† Ù…Ø­Ø§Ø¯Ø«Ø§ØªÙ†Ø§. ÙƒÙ„Ù…Ø§ ØªØ­Ø¯Ø«Ù†Ø§ Ø£ÙƒØ«Ø±ØŒ Ø£ØµØ¨Ø­Øª Ø£ÙØ¶Ù„!"
    ],
    "gemini": [
        "Using advanced AI to answer...",
        "Ø§Ø³ØªØ®Ø¯Ø§Ù… Ø§Ù„Ø°ÙƒØ§Ø¡ Ø§Ù„Ø§ØµØ·Ù†Ø§Ø¹ÙŠ Ø§Ù„Ù…ØªÙ‚Ø¯Ù… Ù„Ù„Ø¥Ø¬Ø§Ø¨Ø©..."
    ],
    "markdown": [
        "I support Markdown formatting! You can use **bold**, *italic*, `code`, lists, and more in your messages.",
        "Ø£Ù†Ø§ Ø£Ø¯Ø¹Ù… ØªÙ†Ø³ÙŠÙ‚ Markdown! ÙŠÙ…ÙƒÙ†Ùƒ Ø§Ø³ØªØ®Ø¯Ø§Ù… **ØºØ§Ù…Ù‚**ØŒ *Ù…Ø§Ø¦Ù„*ØŒ `Ø§Ù„ÙƒÙˆØ¯`ØŒ ÙˆØ§Ù„Ù‚ÙˆØ§Ø¦Ù…ØŒ ÙˆØ§Ù„Ù…Ø²ÙŠØ¯ ÙÙŠ Ø±Ø³Ø§Ø¦Ù„Ùƒ."
    ]
}

# Pattern matching rules
patterns = {
    "greeting": r"(hello|hi|hey|Ù…Ø±Ø­Ø¨Ø§|Ø£Ù‡Ù„Ø§|Ø§Ù„Ø³Ù„Ø§Ù… Ø¹Ù„ÙŠÙƒÙ…)",
    "farewell": r"(goodbye|bye|see you|ÙˆØ¯Ø§Ø¹Ø§|Ù…Ø¹ Ø§Ù„Ø³Ù„Ø§Ù…Ø©)",
    "thanks": r"(thank|thanks|Ø´ÙƒØ±Ø§|Ø´ÙƒØ±Ø§Ù‹)",
    "bot": r"(who are you|what are you|Ù…Ù† Ø£Ù†Øª|Ù…Ø§ Ù‡Ùˆ Ø£Ù†Øª)",
    "capabilities": r"(what can you do|what are your capabilities|Ù…Ø§Ø°Ø§ ÙŠÙ…ÙƒÙ†Ùƒ Ø£Ù† ØªÙØ¹Ù„|Ù…Ø§ Ù‡ÙŠ Ù‚Ø¯Ø±Ø§ØªÙƒ)",
    "weather": r"(weather|forecast|temperature|Ø§Ù„Ø·Ù‚Ø³|Ø¯Ø±Ø¬Ø© Ø§Ù„Ø­Ø±Ø§Ø±Ø©)",
    "time": r"(time|Ø§Ù„ÙˆÙ‚Øª|Ø§Ù„Ø³Ø§Ø¹Ø©)",
    "date": r"(date|today|Ø§Ù„ØªØ§Ø±ÙŠØ®|Ø§Ù„ÙŠÙˆÙ…)",
    "name": r"(your name|Ø§Ø³Ù…Ùƒ)",
    "help": r"(help|Ù…Ø³Ø§Ø¹Ø¯Ø©)",
    "learning": r"(learn:|ØªØ¹Ù„Ù…:)",
    "self_improvement": r"(learn from mistakes|self-learning|improve yourself|ØªØ¹Ù„Ù… Ù…Ù† Ø£Ø®Ø·Ø§Ø¦Ùƒ|Ø§Ù„ØªØ¹Ù„Ù… Ø§Ù„Ø°Ø§ØªÙŠ|ØªØ­Ø³ÙŠÙ† Ù†ÙØ³Ùƒ)",
    "markdown": r"(markdown|formatting|ØªÙ†Ø³ÙŠÙ‚|Ù…Ø§Ø±ÙƒØ¯Ø§ÙˆÙ†)"
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

# Get Gemini-generated response
def get_gemini_response(user_input, session_id, language="english"):
    if not gemini_available:
        return None
    
    try:
        # Get conversation context
        context = get_conversation_context(session_id)
        
        # Get the model to use: from session preference or default
        model_id = session.get('model_preference', config.DEFAULT_GEMINI_MODEL)
        
        # If the model is not available, fallback to any available model
        if model_id not in gemini_models:
            if not gemini_models:  # No models available
                return None
            model_id = next(iter(gemini_models.keys()))
        
        # Create a chat session with context if available
        if context and config.PRESERVE_CONVERSATION_HISTORY:
            chat = gemini_models[model_id].start_chat(history=context)
            response = chat.send_message(user_input)
        else:
            # Construct a more human-like prompt with language preference and markdown capabilities
            if language == "arabic":
                system_prompt = """
                Ø£Ù†Øª Ù…Ø³Ø§Ø¹Ø¯ Ù…Ø­Ø§Ø¯Ø«Ø© Ø°ÙƒÙŠ ÙŠØªØ­Ø¯Ø« Ø¨Ø§Ù„Ù„ØºØ© Ø§Ù„Ø¹Ø±Ø¨ÙŠØ©. Ø£Ø¬Ø¨ Ø¨Ø·Ø±ÙŠÙ‚Ø© Ø·Ø¨ÙŠØ¹ÙŠØ© ÙˆØ¥Ù†Ø³Ø§Ù†ÙŠØ© ÙˆÙ„ÙŠØ³ ÙƒØ±ÙˆØ¨ÙˆØª. 
                Ø§Ø³ØªØ®Ø¯Ù… Ù„ØºØ© Ø¹Ø§Ø¯ÙŠØ© ÙˆÙˆØ§Ø¶Ø­Ø©. Ø§Ø­Ø±Øµ Ø¹Ù„Ù‰ Ø£Ù† ØªÙƒÙˆÙ† Ø¥Ø¬Ø§Ø¨Ø§ØªÙƒ Ù…ÙÙŠØ¯Ø© ÙˆÙˆØ¯ÙŠØ© ÙˆØ¯Ù‚ÙŠÙ‚Ø©.
                Ø¥Ø°Ø§ Ù„Ù… ØªÙƒÙ† Ù…ØªØ£ÙƒØ¯Ù‹Ø§ Ù…Ù† Ø¥Ø¬Ø§Ø¨Ø© Ù…Ø§ØŒ ÙÙ„Ø§ Ø¨Ø£Ø³ Ø£Ù† ØªÙ‚ÙˆÙ„ Ø°Ù„Ùƒ. Ø­Ø§ÙˆÙ„ ØªØ®ØµÙŠØµ Ø¥Ø¬Ø§Ø¨Ø§ØªÙƒ Ø¨Ù†Ø§Ø¡Ù‹ Ø¹Ù„Ù‰ Ø³ÙŠØ§Ù‚ Ø§Ù„Ù…Ø­Ø§Ø¯Ø«Ø©.
                Ø§Ø³ØªØ®Ø¯Ù… ØªÙ†Ø³ÙŠÙ‚ Markdown Ø¹Ù†Ø¯ Ø§Ù„Ø¶Ø±ÙˆØ±Ø©ØŒ Ù…Ø«Ù„ **Ø§Ù„Ù†Øµ Ø§Ù„ØºØ§Ù…Ù‚**ØŒ *Ø§Ù„Ù†Øµ Ø§Ù„Ù…Ø§Ø¦Ù„*ØŒ ÙˆØ§Ù„Ù‚ÙˆØ§Ø¦Ù…ØŒ ÙˆØ±Ù…ÙˆØ² `Ø§Ù„Ø´ÙØ±Ø©`ØŒ ÙˆØ§Ù„Ø¬Ø¯Ø§ÙˆÙ„ØŒ Ø¥Ù„Ø®.
                """
                prompt = f"{system_prompt}\n\nØ§Ù„Ø³Ø¤Ø§Ù„: {user_input}\n\nØ§Ù„Ø¥Ø¬Ø§Ø¨Ø©:"
            else:
                system_prompt = """
                You are an intelligent conversation assistant. Respond naturally and in a human-like manner, not like a robot.
                Use plain, clear language. Make sure your responses are helpful, friendly, and accurate.
                If you're not sure about an answer, it's okay to say so. Try to personalize your responses based on the conversation context.
                Use Markdown formatting where appropriate, such as **bold text**, *italic text*, lists, `code snippets`, tables, etc.
                """
                prompt = f"{system_prompt}\n\nQuestion: {user_input}\n\nResponse:"
            
            response = gemini_models[model_id].generate_content(prompt)
        
        if response and response.text:
            # Remove any "```" code blocks that might be in the response
            cleaned_response = re.sub(r'```.*?```', '', response.text, flags=re.DOTALL)
            cleaned_response = cleaned_response.strip()
            
            # Remove any "Question:" or "Response:" or "Ø§Ù„Ø¥Ø¬Ø§Ø¨Ø©:" prefixes that might be in the response
            cleaned_response = re.sub(r'^(Question:|Response:|Ø§Ù„Ø¥Ø¬Ø§Ø¨Ø©:|Ø§Ù„Ø¬ÙˆØ§Ø¨:)\s*', '', cleaned_response, flags=re.IGNORECASE)
            
            # Limit length if needed
            if len(cleaned_response) > 800:
                cleaned_response = cleaned_response[:797] + "..."
                
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
    learning_pattern = re.compile(r'^(learn:|ØªØ¹Ù„Ù…:)\s*(.*)', re.IGNORECASE)
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
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    
    conversation_memory[session_id].append({
        "role": role,
        "message": message,
        "timestamp": time.time()
    })
    
    # Limit conversation history to last 30 messages
    if len(conversation_memory[session_id]) > 30:
        conversation_memory[session_id] = conversation_memory[session_id][-30:]
    
    save_conversation_memory(conversation_memory)

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
        f"Ø§Ù„ÙˆÙ‚Øª Ø§Ù„Ø­Ø§Ù„ÙŠ Ù„Ù„Ø®Ø§Ø¯Ù… Ù‡Ùˆ {time.strftime('%H:%M:%S')}"
    ]
    responses["date"] = [
        f"Today is {time.strftime('%Y-%m-%d')}",
        f"Ø§Ù„ÙŠÙˆÙ… Ù‡Ùˆ {time.strftime('%Y-%m-%d')}"
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

@app.route('/')
def home():
    # Generate a unique session ID if one doesn't exist
    if 'session_id' not in session:
        session['session_id'] = str(time.time())
    
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get or create session ID
    session_id = session.get('session_id', str(time.time()))
    if 'session_id' not in session:
        session['session_id'] = session_id
    
    # Add a small delay to simulate thinking
    time.sleep(config.THINKING_DELAY)
    
    bot_response = get_response(user_message, session_id)
    
    # Process markdown if enabled
    if config.ENABLE_MARKDOWN:
        bot_response_html = parse_markdown(bot_response)
    else:
        bot_response_html = bot_response
    
    return jsonify({
        'response': bot_response,
        'response_html': bot_response_html,
        'has_markdown': config.ENABLE_MARKDOWN and bot_response != bot_response_html
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
        "markdown_enabled": config.ENABLE_MARKDOWN,
        "available_models": list(gemini_models.keys()) if gemini_models else [],
        "current_model": session.get('model_preference', config.DEFAULT_GEMINI_MODEL),
        "model_info": config.GEMINI_MODELS
    }
    return jsonify(stats)

# Get statistics
@app.route('/get_statistics', methods=['GET'])
def get_statistics():
    stats = {
        "learned_responses": len(learning_memory["user_corrections"]),
        "conversation_sessions": len(conversation_memory),
        "popular_topics": get_popular_topics(),
        "stats_over_time": get_stats_over_time(),
        "available_models": list(gemini_models.keys()) if gemini_models else [],
        "current_model": session.get('model_preference', config.DEFAULT_GEMINI_MODEL)
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

# Get all conversations
@app.route('/get_conversations', methods=['GET'])
def get_conversations():
    result = {"conversations": []}
    
    # Get conversation from memory
    for session_id, conversation in conversation_memory.items():
        if not conversation:
            continue
        
        # Get the first message from user as title
        first_user_message = next((msg["message"] for msg in conversation if msg["role"] == "user"), "")
        title = first_user_message[:30] + "..." if len(first_user_message) > 30 else first_user_message
        
        # Get the last message as preview
        last_message = conversation[-1]["message"] if conversation else ""
        preview = last_message[:30] + "..." if len(last_message) > 30 else last_message
        
        result["conversations"].append({
            "id": session_id,
            "title": title or "New conversation",
            "preview": preview or "No messages",
            "timestamp": conversation[-1].get("timestamp", 0) if conversation else 0
        })
    
    # Sort by timestamp, newest first
    result["conversations"].sort(key=lambda x: x["timestamp"], reverse=True)
    
    return jsonify(result)

# Get a specific conversation
@app.route('/get_conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    # Return conversation messages from session storage
    if conversation_id in conversation_memory:
        return jsonify({"messages": conversation_memory[conversation_id]})
    return jsonify({"messages": []})

# Send message - updated endpoint 
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_input = data.get('message', '')
    conversation_id = data.get('conversation_id', '')
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    
    # Create session if doesn't exist
    if not conversation_id or conversation_id not in conversation_memory:
        conversation_id = f"conv_{int(time.time())}"
        conversation_memory[conversation_id] = []
    
    # Process message and get response
    response = get_response(user_input, conversation_id)
    
    # Save updated memory
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
        "stats": stats
    })

# New endpoint to select model
@app.route('/select_model', methods=['POST'])
def select_model():
    data = request.json
    model_id = data.get('model_id')
    
    if not model_id:
        return jsonify({"error": "No model ID provided"}), 400
    
    # Validate that the model exists
    if model_id not in config.GEMINI_MODELS:
        return jsonify({"error": "Invalid model ID"}), 400
    
    # Check if model is available
    model_available = model_id in gemini_models
    
    # Save the preference in session
    session['model_preference'] = model_id
    
    return jsonify({
        "success": True,
        "model": model_id,
        "model_name": config.GEMINI_MODELS[model_id]["name"],
        "available": model_available
    })

# Firebase proxy routes - these allow secure access to Firebase from the client
# without exposing API keys directly

@app.route('/api/firebase/verify_token', methods=['POST'])
def verify_firebase_token():
    """Verify a Firebase ID token - this is a security measure for server-side validation"""
    try:
        data = request.json
        token = data.get('token')
        
        # Here you would verify the token with Firebase Admin SDK
        # For this example, we'll just return success
        # In a production environment, you would need to:
        # 1. Initialize Firebase Admin SDK
        # 2. Use auth.verify_id_token(token)
        # 3. Return the decoded claims or an error
        
        return jsonify({"success": True, "uid": "example_uid_from_token"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Add API endpoint to handle messages in Firebase format
@app.route('/api/firebase/send_message', methods=['POST'])
def firebase_send_message():
    """Process messages from Firebase users and maintain conversation context"""
    try:
        data = request.json
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', '')
        user_id = data.get('user_id', '')
        
        if not message or not conversation_id or not user_id:
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Process message using the chatbot's engine
        response = process_message(message, conversation_id)
        
        return jsonify({
            "response": response,
            "conversation_id": conversation_id,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route('/api/firebase/user_settings', methods=['GET', 'POST'])
def user_settings():
    """Get or update user settings"""
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400
            
        # Here you would fetch user settings from your database
        # For this example, we'll return default settings
        return jsonify({
            "theme": "light",
            "language_preference": config.DEFAULT_LANGUAGE,
            "notifications_enabled": True
        })
    else:  # POST
        try:
            data = request.json
            user_id = data.get('user_id')
            settings = data.get('settings', {})
            
            if not user_id:
                return jsonify({"error": "Missing user_id parameter"}), 400
                
            # Here you would update the user settings in your database
            # For this example, we'll just return success
            return jsonify({"success": True, "message": "Settings updated"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG) 
