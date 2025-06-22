#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_delete_with_auth():
    """Test deleting a conversation with simulated authentication"""
    
    # Test with one of the conversation IDs from the error log
    conversation_id = "1750555615167.2669970593247787"
    
    print(f"🧪 Testing delete conversation API with authentication...")
    print(f"📋 Conversation ID: {conversation_id}")
    print("-" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Login to establish session
    print("🔐 Step 1: Logging in to establish session...")
    login_url = "http://localhost:5000/save_user_session"
    login_data = {
        "user_id": "6kvxle04mBSrAg8weJyCgOUOgYz1",  # The user ID from the file path
        "email": "etest0385@gmail.com"
    }
    
    try:
        login_response = session.post(login_url, json=login_data, timeout=10)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Login successful!")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"   💥 Login error: {e}")
        return
    
    # Step 2: Test delete conversation
    print("\n🗑️ Step 2: Testing delete conversation...")
    delete_url = "http://localhost:5000/delete_conversation"
    delete_data = {
        "conversation_id": conversation_id
    }
    
    try:
        response = session.post(delete_url, json=delete_data, timeout=10)
        
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   📝 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ SUCCESS: Conversation deleted successfully!")
            else:
                print(f"   ❌ ERROR: Delete failed - {data}")
        else:
            print(f"   ❌ HTTP ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw response: {response.text}")
                
    except Exception as e:
        print(f"   💥 Exception: {e}")
    
    # Step 3: Verify deletion by trying to load the conversation
    print("\n🔍 Step 3: Verifying deletion...")
    get_url = f"http://localhost:5000/get_conversation/{conversation_id}"
    
    try:
        verify_response = session.get(get_url, timeout=10)
        print(f"   Verification Status: {verify_response.status_code}")
        
        if verify_response.status_code == 404:
            print("   ✅ VERIFIED: Conversation successfully deleted (404 as expected)")
        elif verify_response.status_code == 200:
            print("   ⚠️ WARNING: Conversation still exists!")
        else:
            print(f"   ❓ Unexpected status: {verify_response.status_code}")
            
    except Exception as e:
        print(f"   💥 Verification error: {e}")

if __name__ == "__main__":
    test_delete_with_auth() 