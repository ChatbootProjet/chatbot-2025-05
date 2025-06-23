#!/usr/bin/env python3
"""
Simple test runner for the AI Chatbot
"""

import os
import sys
import traceback

def main():
    try:
        print("🔧 Testing AI Chatbot startup...")
        print("📁 Current directory:", os.getcwd())
        
        # Test imports
        print("📦 Testing imports...")
        
        try:
            import flask
            print("✅ Flask imported successfully")
        except ImportError as e:
            print(f"❌ Flask import failed: {e}")
            return 1
            
        try:
            import google.generativeai as genai
            print("✅ Google GenerativeAI imported successfully")
        except ImportError as e:
            print(f"❌ Google GenerativeAI import failed: {e}")
            print("💡 Install with: pip install google-generativeai")
            return 1
        
        # Test app import
        print("🤖 Testing app import...")
        try:
            from app import app
            print("✅ App imported successfully")
        except Exception as e:
            print(f"❌ App import failed: {e}")
            traceback.print_exc()
            return 1
        
        # Try to start the app
        print("🚀 Starting Flask app on port 5000...")
        print("📱 Access at: http://localhost:5000")
        print("🌍 Network access: http://[YOUR-IP]:5000")
        print("⏹️  Press Ctrl+C to stop")
        print("-" * 50)
        
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid double startup
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except PermissionError as e:
        print(f"❌ Permission error: {e}")
        print("💡 Try running as Administrator or use a different port")
        return 1
    except OSError as e:
        if "10013" in str(e):
            print("❌ Port 5000 is already in use or requires special permissions")
            print("💡 Try closing other applications or use a different port")
        else:
            print(f"❌ OS Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 