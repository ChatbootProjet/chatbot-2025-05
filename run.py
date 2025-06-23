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
    
    # Try to start on port 80 first, then fallback to 5000
    try:
        print("Attempting to start on port 80 (HTTP default)...")
        
        # Open web browser
        url = "http://localhost"
        webbrowser.open(url)
        
        # Run the app with global accessibility on HTTP default port
        app.run(host="0.0.0.0", port=80, debug=True)
        
    except PermissionError:
        print("\n⚠️  Permission denied for port 80. This port requires Administrator privileges.")
        print("💡 Solution: Run as Administrator or use a different port.")
        print("🔄 Falling back to port 5000...")
        
        # Open web browser with port 5000
        url = "http://localhost:5000"
        webbrowser.open(url)
        
        # Run on port 5000 as fallback
        app.run(host="0.0.0.0", port=5000, debug=True)
        
    except OSError as e:
        if "10013" in str(e) or "Permission denied" in str(e):
            print("\n⚠️  Port 80 is already in use or requires Administrator privileges.")
            print("💡 This might be IIS, Apache, or another web server.")
            print("🔄 Falling back to port 5000...")
            
            # Open web browser with port 5000
            url = "http://localhost:5000"
            webbrowser.open(url)
            
            # Run on port 5000 as fallback
            app.run(host="0.0.0.0", port=5000, debug=True)
        else:
            print(f"\n❌ Error starting server: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 