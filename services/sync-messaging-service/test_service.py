"""
EduNerve Sync & Messaging Service - Test Script
Comprehensive testing of sync, messaging, and real-time features
"""

import requests
import json
import asyncio
import websockets
import time
from datetime import datetime
from typing import Dict, Any

# Service configuration
BASE_URL = "http://localhost:8004"
WS_URL = "ws://localhost:8004"

# Test user credentials (would come from auth service in real scenario)
TEST_USER = {
    "user_id": 1,
    "school_id": 1,
    "token": "test-jwt-token-for-user-1"
}

class SyncMessagingServiceTester:
    """Test class for Sync & Messaging Service"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.ws_url = WS_URL
        self.headers = {
            "Authorization": f"Bearer {TEST_USER['token']}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("🏥 Testing health check...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def test_device_registration(self):
        """Test device registration"""
        print("\n📱 Testing device registration...")
        
        try:
            device_data = {
                "device_id": "test-device-001",
                "user_id": TEST_USER["user_id"],
                "school_id": TEST_USER["school_id"],
                "device_type": "mobile",
                "platform": "android",
                "app_version": "1.0.0",
                "os_version": "11.0",
                "fcm_token": "test-fcm-token-123",
                "sync_enabled": True,
                "sync_settings": {"auto_sync": True, "sync_interval": 300}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/devices/register",
                json=device_data
            )
            
            if response.status_code == 200:
                device = response.json()
                print(f"✅ Device registered: {device['device_id']}")
                return device
            else:
                print(f"❌ Device registration failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Device registration error: {str(e)}")
            return None
    
    def test_sync_record_creation(self):
        """Test sync record creation"""
        print("\n🔄 Testing sync record creation...")
        
        try:
            sync_data = {
                "user_id": TEST_USER["user_id"],
                "school_id": TEST_USER["school_id"],
                "device_id": "test-device-001",
                "entity_type": "quiz_attempt",
                "entity_id": "quiz_001",
                "operation": "create",
                "data": {
                    "quiz_id": "quiz_001",
                    "user_id": TEST_USER["user_id"],
                    "answers": [
                        {"question_id": "q1", "answer": "A", "is_correct": True},
                        {"question_id": "q2", "answer": "B", "is_correct": False}
                    ],
                    "score": 50,
                    "completed_at": datetime.now().isoformat()
                },
                "metadata": {"offline_created": True, "retry_count": 0},
                "priority": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/sync/records",
                json=sync_data
            )
            
            if response.status_code == 200:
                sync_record = response.json()
                print(f"✅ Sync record created: {sync_record['sync_id']}")
                return sync_record
            else:
                print(f"❌ Sync record creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Sync record creation error: {str(e)}")
            return None
    
    def test_sync_processing(self, sync_id: str):
        """Test sync record processing"""
        print(f"\n⚡ Testing sync processing for {sync_id}...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/sync/process/{sync_id}"
            )
            
            if response.status_code == 200:
                sync_record = response.json()
                print(f"✅ Sync processed: {sync_record['status']}")
                return sync_record
            else:
                print(f"❌ Sync processing failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Sync processing error: {str(e)}")
            return None
    
    def test_bulk_sync(self):
        """Test bulk synchronization"""
        print("\n📦 Testing bulk sync...")
        
        try:
            bulk_request = {
                "device_id": "test-device-001",
                "user_id": TEST_USER["user_id"],
                "school_id": TEST_USER["school_id"],
                "sync_records": [
                    {
                        "user_id": TEST_USER["user_id"],
                        "school_id": TEST_USER["school_id"],
                        "device_id": "test-device-001",
                        "entity_type": "user_progress",
                        "entity_id": "progress_001",
                        "operation": "update",
                        "data": {"module_id": "mod_001", "progress": 75, "last_accessed": datetime.now().isoformat()},
                        "priority": 2
                    },
                    {
                        "user_id": TEST_USER["user_id"],
                        "school_id": TEST_USER["school_id"],
                        "device_id": "test-device-001",
                        "entity_type": "study_session",
                        "entity_id": "session_001",
                        "operation": "create",
                        "data": {"subject": "Mathematics", "duration": 1800, "topics": ["algebra", "geometry"]},
                        "priority": 1
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/sync/bulk",
                json=bulk_request
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Bulk sync completed: {result['processed']}/{result['total']} processed")
                return result
            else:
                print(f"❌ Bulk sync failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Bulk sync error: {str(e)}")
            return None
    
    def test_message_sending(self):
        """Test message sending"""
        print("\n💬 Testing message sending...")
        
        try:
            message_data = {
                "message_type": "chat",
                "subject": "Test Message",
                "content": "Hello! This is a test message from the sync-messaging service.",
                "sender_id": TEST_USER["user_id"],
                "sender_name": "Test User",
                "sender_type": "student",
                "recipient_ids": [2, 3],  # Other test users
                "school_id": TEST_USER["school_id"],
                "context": {"test": True, "timestamp": datetime.now().isoformat()},
                "thread_id": "thread_001"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/messages",
                json=message_data
            )
            
            if response.status_code == 200:
                message = response.json()
                print(f"✅ Message sent: {message['message_id']}")
                return message
            else:
                print(f"❌ Message sending failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Message sending error: {str(e)}")
            return None
    
    def test_notification_sending(self):
        """Test notification sending"""
        print("\n🔔 Testing notification sending...")
        
        try:
            notification_data = {
                "title": "Test Notification",
                "body": "This is a test push notification from the sync-messaging service.",
                "notification_type": "info",
                "category": "general",
                "user_id": TEST_USER["user_id"],
                "school_id": TEST_USER["school_id"],
                "device_tokens": ["test-fcm-token-123"],
                "data": {"action": "open_app", "screen": "dashboard"},
                "action_url": "/dashboard"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/notifications",
                json=notification_data
            )
            
            if response.status_code == 200:
                notification = response.json()
                print(f"✅ Notification sent: {notification['notification_id']}")
                return notification
            else:
                print(f"❌ Notification sending failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Notification sending error: {str(e)}")
            return None
    
    def test_offline_data_storage(self):
        """Test offline data storage"""
        print("\n💾 Testing offline data storage...")
        
        try:
            offline_data = {
                "user_id": TEST_USER["user_id"],
                "device_id": "test-device-001",
                "school_id": TEST_USER["school_id"],
                "entity_type": "quiz_content",
                "entity_id": "quiz_001",
                "data": {
                    "quiz_title": "Mathematics Quiz 1",
                    "questions": [
                        {"id": "q1", "question": "What is 2+2?", "options": ["3", "4", "5", "6"], "correct": 1},
                        {"id": "q2", "question": "What is 3×3?", "options": ["6", "9", "12", "15"], "correct": 1}
                    ],
                    "time_limit": 1800,
                    "passing_score": 70
                },
                "cache_key": "quiz_001_content",
                "cache_duration": 86400,
                "is_encrypted": False
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/offline/store",
                json=offline_data
            )
            
            if response.status_code == 200:
                stored_data = response.json()
                print(f"✅ Offline data stored: {stored_data['data_id']}")
                return stored_data
            else:
                print(f"❌ Offline data storage failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Offline data storage error: {str(e)}")
            return None
    
    def test_sync_status(self):
        """Test sync status retrieval"""
        print("\n📊 Testing sync status...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/sync/status?device_id=test-device-001"
            )
            
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Sync status retrieved: {status['pending_syncs']} pending, {status['conflicts']} conflicts")
                return status
            else:
                print(f"❌ Sync status retrieval failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Sync status error: {str(e)}")
            return None
    
    def test_get_messages(self):
        """Test message retrieval"""
        print("\n📬 Testing message retrieval...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/messages?limit=10"
            )
            
            if response.status_code == 200:
                messages = response.json()
                print(f"✅ Retrieved {len(messages)} messages")
                return messages
            else:
                print(f"❌ Message retrieval failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Message retrieval error: {str(e)}")
            return None
    
    def test_get_notifications(self):
        """Test notification retrieval"""
        print("\n🔔 Testing notification retrieval...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/notifications?limit=10"
            )
            
            if response.status_code == 200:
                notifications = response.json()
                print(f"✅ Retrieved {len(notifications)} notifications")
                return notifications
            else:
                print(f"❌ Notification retrieval failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Notification retrieval error: {str(e)}")
            return None
    
    async def test_websocket_connection(self):
        """Test WebSocket real-time communication"""
        print("\n🌐 Testing WebSocket connection...")
        
        try:
            uri = f"{self.ws_url}/ws/{TEST_USER['user_id']}?token={TEST_USER['token']}"
            
            async with websockets.connect(uri) as websocket:
                print("✅ WebSocket connection established")
                
                # Send ping
                ping_message = {"type": "ping", "data": {}}
                await websocket.send(json.dumps(ping_message))
                
                # Receive pong
                response = await websocket.recv()
                pong_data = json.loads(response)
                
                if pong_data.get("type") == "pong":
                    print("✅ WebSocket ping/pong successful")
                
                # Send subscription
                subscribe_message = {
                    "type": "subscribe",
                    "data": {"topic": "thread_001"}
                }
                await websocket.send(json.dumps(subscribe_message))
                
                # Wait for subscription confirmation
                response = await websocket.recv()
                sub_data = json.loads(response)
                
                if sub_data.get("type") == "subscription_result":
                    print("✅ WebSocket subscription successful")
                
                # Send a test message
                chat_message = {
                    "type": "send_message",
                    "data": {
                        "recipient_ids": [2, 3],
                        "content": "Hello from WebSocket!",
                        "thread_id": "thread_001"
                    }
                }
                await websocket.send(json.dumps(chat_message))
                print("✅ WebSocket message sent")
                
                return True
                
        except Exception as e:
            print(f"❌ WebSocket test error: {str(e)}")
            return False
    
    def test_get_service_stats(self):
        """Test service statistics (admin endpoint)"""
        print("\n📈 Testing service statistics...")
        
        try:
            # Note: This would require admin token in real scenario
            response = self.session.get(f"{self.base_url}/api/v1/stats")
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Service stats retrieved:")
                print(f"   - Total syncs: {stats['sync_stats']['total_syncs']}")
                print(f"   - Pending syncs: {stats['sync_stats']['pending_syncs']}")
                print(f"   - Total messages: {stats['messaging_stats']['total_messages']}")
                print(f"   - Active devices: {stats['active_devices']}")
                return stats
            else:
                print(f"❌ Service stats failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Service stats error: {str(e)}")
            return None
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting EduNerve Sync & Messaging Service Tests\n")
        
        test_results = []
        
        # Basic tests
        test_results.append(("Health Check", self.test_health_check()))
        test_results.append(("Device Registration", self.test_device_registration() is not None))
        
        # Sync tests
        sync_record = self.test_sync_record_creation()
        test_results.append(("Sync Record Creation", sync_record is not None))
        
        if sync_record:
            processed_sync = self.test_sync_processing(sync_record["sync_id"])
            test_results.append(("Sync Processing", processed_sync is not None))
        
        test_results.append(("Bulk Sync", self.test_bulk_sync() is not None))
        test_results.append(("Sync Status", self.test_sync_status() is not None))
        
        # Messaging tests
        test_results.append(("Message Sending", self.test_message_sending() is not None))
        test_results.append(("Get Messages", self.test_get_messages() is not None))
        
        # Notification tests
        test_results.append(("Notification Sending", self.test_notification_sending() is not None))
        test_results.append(("Get Notifications", self.test_get_notifications() is not None))
        
        # Offline data tests
        test_results.append(("Offline Data Storage", self.test_offline_data_storage() is not None))
        
        # WebSocket test
        try:
            websocket_result = asyncio.run(self.test_websocket_connection())
            test_results.append(("WebSocket Connection", websocket_result))
        except Exception as e:
            print(f"❌ WebSocket test skipped: {str(e)}")
            test_results.append(("WebSocket Connection", False))
        
        # Admin tests
        test_results.append(("Service Stats", self.test_get_service_stats() is not None))
        
        # Print summary
        print(f"\n{'='*50}")
        print("🎯 TEST SUMMARY")
        print(f"{'='*50}")
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Sync & Messaging Service is working correctly.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Please check the service configuration.")
        
        return passed == total

def main():
    """Main test function"""
    print("EduNerve Sync & Messaging Service - Test Suite")
    print("=" * 50)
    
    # Wait a bit for service to be ready
    print("⏳ Waiting for service to be ready...")
    time.sleep(2)
    
    # Create tester and run tests
    tester = SyncMessagingServiceTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All tests completed successfully!")
        exit(0)
    else:
        print("\n❌ Some tests failed!")
        exit(1)

if __name__ == "__main__":
    main()
