import requests
import json

def test_conversation_api():
    """Test the conversation loading API"""
    
    # Test conversation IDs from the error log
    conversation_ids = [
        "1750555615167.2669970593247787",
        "1750555638400.9663244229596664", 
        "1750530107576.3095791681765713"
    ]
    
    print("🧪 Testing Conversation API Endpoints...")
    print("=" * 50)
    
    for conv_id in conversation_ids:
        print(f"\n📋 Testing conversation: {conv_id}")
        
        try:
            # Test the API endpoint
            url = f"http://localhost:5000/get_conversation/{conv_id}"
            response = requests.get(url, timeout=5)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS: Found {len(data.get('messages', []))} messages")
                
                # Show first message preview
                if data.get('messages'):
                    first_msg = data['messages'][0]
                    preview = first_msg.get('text', '')[:50]
                    print(f"   📝 First message: {preview}...")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"   ❌ ERROR: {error_data}")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Connection Error: {e}")
        except Exception as e:
            print(f"   🚨 Unexpected Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_conversation_api() 