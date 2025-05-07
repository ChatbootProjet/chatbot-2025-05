#!/usr/bin/env python
"""
Run script for the AI Chatbot

This script checks for dependencies and starts the application.
It provides a simple way to run the chatbot from the command line.
"""

import os
import sys
import subprocess
import webbrowser
import config

def check_dependencies():
    """Check if all required packages are installed."""
    try:
        import flask
        import nltk
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install dependencies using: pip install -r requirements.txt")
        return False

def main():
    """Main function to start the application."""
    print("Starting AI Chatbot...")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Start the Flask app
    from app import app
    
    # Open web browser
    url = f"http://{'localhost' if config.HOST == '0.0.0.0' else config.HOST}:{config.PORT}"
    webbrowser.open(url)
    
    # Run the app
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 