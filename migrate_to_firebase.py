#!/usr/bin/env python3
"""
🔥 Firebase Migration Script
نقل البيانات من Local Storage إلى Firebase

هذا السكريبت ينقل:
1. المحادثات من data/users/{userId}/conversations.json إلى Firebase
2. بيانات المستخدمين إلى Firebase بالهيكل الجديد
3. التحقق من سلامة البيانات بعد النقل

الاستخدام:
python migrate_to_firebase.py
"""

import os
import json
import time
import sys
from pathlib import Path

# Add current directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import firebase_admin
    from firebase_admin import credentials, db
    import config
except ImportError as e:
    print(f"❌ خطأ في استيراد المكتبات: {e}")
    print("💡 تأكد من تثبيت المكتبات المطلوبة:")
    print("pip install firebase-admin")
    sys.exit(1)

def init_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase is already initialized
        try:
            firebase_admin.get_app()
            print("✅ Firebase already initialized")
            return True
        except ValueError:
            pass
        
        # Initialize Firebase
        if not os.path.exists(config.FIREBASE_SERVICE_ACCOUNT_PATH):
            print(f"❌ Firebase service account file not found: {config.FIREBASE_SERVICE_ACCOUNT_PATH}")
            print("💡 Please set up Firebase credentials first")
            return False
        
        # Check if it's a dummy file
        with open(config.FIREBASE_SERVICE_ACCOUNT_PATH, 'r') as f:
            content = f.read()
            if 'YOUR_PROJECT_ID' in content or 'your-private-key' in content:
                print("❌ Firebase service account file appears to be a template")
                print("💡 Please replace with actual Firebase credentials")
                return False
        
        cred = credentials.Certificate(config.FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': f'https://{config.FIREBASE_PROJECT_ID}-default-rtdb.firebaseio.com/'
        })
        
        print("✅ Firebase initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False

def load_user_conversations_locally(user_id):
    """Load user conversations from local storage"""
    user_dir = Path(f"data/users/{user_id}")
    conversations_file = user_dir / "conversations.json"
    
    if not conversations_file.exists():
        return {}
    
    try:
        with open(conversations_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading conversations for user {user_id}: {e}")
        return {}

def migrate_user_conversations(user_id, conversations):
    """Migrate user conversations to Firebase"""
    try:
        migrated_count = 0
        
        for conv_id, conv_data in conversations.items():
            # Convert old format to new format if needed
            if isinstance(conv_data, list):
                # Old format: just messages array
                messages = conv_data
                conversation_data = {
                    'messages': messages,
                    'title': 'New Conversation',
                    'timestamp': messages[-1].get('timestamp', time.time()) if messages else time.time(),
                    'createdAt': messages[0].get('timestamp', time.time()) if messages else time.time(),
                    'updatedAt': time.time(),
                    'messageCount': len(messages),
                    'lastMessage': ''
                }
                
                # Generate title from first user message
                first_user_msg = next((msg for msg in messages if msg.get('role') == 'user'), None)
                if first_user_msg:
                    title = first_user_msg['message'][:30]
                    if len(first_user_msg['message']) > 30:
                        title += "..."
                    conversation_data['title'] = title
                
                # Get last message for preview
                for msg in reversed(messages):
                    if msg.get('role') == 'user':
                        conversation_data['lastMessage'] = msg.get('message', '')[:100]
                        break
                        
            else:
                # New format: conversation object
                conversation_data = {
                    'messages': conv_data.get('messages', []),
                    'title': conv_data.get('title', 'New Conversation'),
                    'timestamp': conv_data.get('timestamp', time.time()),
                    'createdAt': conv_data.get('createdAt', time.time()),
                    'updatedAt': time.time(),
                    'messageCount': len(conv_data.get('messages', [])),
                    'lastMessage': conv_data.get('lastMessage', '')
                }
                
                # Generate lastMessage if not present
                if not conversation_data['lastMessage']:
                    messages = conversation_data['messages']
                    for msg in reversed(messages):
                        if msg.get('role') == 'user':
                            conversation_data['lastMessage'] = msg.get('message', '')[:100]
                            break
            
            # Save to Firebase
            ref = db.reference(f'users/{user_id}/conversations/{conv_id}')
            ref.set(conversation_data)
            migrated_count += 1
            
            print(f"  ✅ Migrated conversation: {conversation_data['title'][:50]}")
        
        return migrated_count
        
    except Exception as e:
        print(f"❌ Error migrating conversations for user {user_id}: {e}")
        return 0

def create_user_profile_in_firebase(user_id):
    """Create a basic user profile in Firebase"""
    try:
        profile_data = {
            'uid': user_id,
            'createdAt': time.time(),
            'lastActivity': time.time(),
            'provider': 'migrated',
            'displayName': f'User {user_id[:8]}',
            'email': '',
            'photoURL': ''
        }
        
        ref = db.reference(f'users/{user_id}/profile')
        ref.set(profile_data)
        
        print(f"  ✅ Created profile for user {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating profile for user {user_id}: {e}")
        return False

def get_all_local_users():
    """Get all users with local data"""
    users_dir = Path("data/users")
    if not users_dir.exists():
        return []
    
    users = []
    for user_dir in users_dir.iterdir():
        if user_dir.is_dir() and (user_dir / "conversations.json").exists():
            users.append(user_dir.name)
    
    return users

def verify_migration(user_id, original_count):
    """Verify that migration was successful"""
    try:
        ref = db.reference(f'users/{user_id}/conversations')
        firebase_conversations = ref.get() or {}
        
        firebase_count = len(firebase_conversations)
        
        if firebase_count == original_count:
            print(f"  ✅ Verification passed: {firebase_count} conversations migrated")
            return True
        else:
            print(f"  ❌ Verification failed: Expected {original_count}, found {firebase_count}")
            return False
            
    except Exception as e:
        print(f"  ❌ Verification error: {e}")
        return False

def main():
    """Main migration function"""
    print("🔥 Firebase Migration Script")
    print("=" * 50)
    
    # Initialize Firebase
    if not init_firebase():
        print("❌ Cannot proceed without Firebase connection")
        return
    
    # Get all users with local data
    users = get_all_local_users()
    if not users:
        print("ℹ️ No local user data found to migrate")
        return
    
    print(f"📊 Found {len(users)} users with local data")
    print()
    
    total_conversations = 0
    successful_users = 0
    
    for user_id in users:
        print(f"👤 Migrating user: {user_id}")
        
        # Load local conversations
        conversations = load_user_conversations_locally(user_id)
        original_count = len(conversations)
        
        if original_count == 0:
            print(f"  ℹ️ No conversations found for user {user_id}")
            continue
        
        print(f"  📝 Found {original_count} conversations")
        
        # Create user profile
        create_user_profile_in_firebase(user_id)
        
        # Migrate conversations
        migrated_count = migrate_user_conversations(user_id, conversations)
        
        if migrated_count > 0:
            # Verify migration
            if verify_migration(user_id, original_count):
                total_conversations += migrated_count
                successful_users += 1
                print(f"  ✅ User {user_id} migrated successfully")
            else:
                print(f"  ❌ User {user_id} migration verification failed")
        else:
            print(f"  ❌ User {user_id} migration failed")
        
        print()
    
    # Summary
    print("📊 Migration Summary")
    print("=" * 30)
    print(f"👥 Users processed: {len(users)}")
    print(f"✅ Users migrated successfully: {successful_users}")
    print(f"💬 Total conversations migrated: {total_conversations}")
    
    if successful_users == len(users):
        print("🎉 Migration completed successfully!")
        
        # Ask about backup cleanup
        response = input("\n🗑️ Do you want to create a backup of local data before cleanup? (y/N): ")
        if response.lower() in ['y', 'yes']:
            backup_local_data()
            
        cleanup_response = input("🧹 Do you want to clean up local data files? (y/N): ")
        if cleanup_response.lower() in ['y', 'yes']:
            cleanup_local_data()
    else:
        print("⚠️ Migration completed with some errors. Check the logs above.")

def backup_local_data():
    """Create a backup of local data"""
    try:
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"data_backup_{timestamp}"
        
        shutil.copytree("data/users", f"{backup_dir}/users")
        print(f"✅ Backup created: {backup_dir}")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def cleanup_local_data():
    """Clean up local data files after successful migration"""
    try:
        import shutil
        
        users_dir = Path("data/users")
        if users_dir.exists():
            shutil.rmtree(users_dir)
            print("✅ Local user data cleaned up")
        
        # Also clean up old conversation memory files
        old_files = [
            "data/conversation_memory.json",
            "data/conversation_memory_backup.json"
        ]
        
        for file_path in old_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    main() 