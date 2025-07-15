"""
EduNerve Sync & Messaging Service - WebSocket Manager
Real-time communication and event handling
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
import json
import logging
import asyncio
from datetime import datetime
import uuid

from .models import WebSocketConnection
from .schemas import RealTimeEvent, WebSocketMessage
from .auth import CurrentUser

# Configure logging
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Active connections by connection_id
        self.active_connections: Dict[str, WebSocket] = {}
        
        # User to connections mapping
        self.user_connections: Dict[int, List[str]] = {}
        
        # School to connections mapping
        self.school_connections: Dict[int, List[str]] = {}
        
        # Topic subscriptions
        self.topic_subscriptions: Dict[str, List[str]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user: CurrentUser
    ):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Store connection
            self.active_connections[connection_id] = websocket
            
            # Add to user connections
            if user.user_id not in self.user_connections:
                self.user_connections[user.user_id] = []
            self.user_connections[user.user_id].append(connection_id)
            
            # Add to school connections
            if user.school_id not in self.school_connections:
                self.school_connections[user.school_id] = []
            self.school_connections[user.school_id].append(connection_id)
            
            logger.info(f"WebSocket connection {connection_id} established for user {user.user_id}")
            
            # Send welcome message
            await self.send_personal_message({
                "type": "connection_established",
                "data": {
                    "connection_id": connection_id,
                    "user_id": user.user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }, connection_id)
            
        except Exception as e:
            logger.error(f"Error establishing WebSocket connection: {str(e)}")
            raise
    
    def disconnect(self, connection_id: str, user_id: int, school_id: int):
        """Handle WebSocket disconnection"""
        try:
            # Remove from active connections
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            
            # Remove from user connections
            if user_id in self.user_connections:
                if connection_id in self.user_connections[user_id]:
                    self.user_connections[user_id].remove(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from school connections
            if school_id in self.school_connections:
                if connection_id in self.school_connections[school_id]:
                    self.school_connections[school_id].remove(connection_id)
                if not self.school_connections[school_id]:
                    del self.school_connections[school_id]
            
            # Remove from topic subscriptions
            for topic, connections in self.topic_subscriptions.items():
                if connection_id in connections:
                    connections.remove(connection_id)
            
            # Clean up empty topics
            self.topic_subscriptions = {
                topic: connections 
                for topic, connections in self.topic_subscriptions.items() 
                if connections
            }
            
            logger.info(f"WebSocket connection {connection_id} disconnected for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling WebSocket disconnection: {str(e)}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send message to a specific connection"""
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error sending personal message to {connection_id}: {str(e)}")
            # Remove broken connection
            await self._remove_broken_connection(connection_id)
            return False
    
    async def send_user_message(self, message: Dict[str, Any], user_id: int):
        """Send message to all connections of a user"""
        try:
            if user_id not in self.user_connections:
                return 0
            
            connections = self.user_connections[user_id].copy()
            sent_count = 0
            
            for connection_id in connections:
                success = await self.send_personal_message(message, connection_id)
                if success:
                    sent_count += 1
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending user message to user {user_id}: {str(e)}")
            return 0
    
    async def send_school_message(self, message: Dict[str, Any], school_id: int):
        """Send message to all connections in a school"""
        try:
            if school_id not in self.school_connections:
                return 0
            
            connections = self.school_connections[school_id].copy()
            sent_count = 0
            
            for connection_id in connections:
                success = await self.send_personal_message(message, connection_id)
                if success:
                    sent_count += 1
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending school message to school {school_id}: {str(e)}")
            return 0
    
    async def send_topic_message(self, message: Dict[str, Any], topic: str):
        """Send message to all subscribers of a topic"""
        try:
            if topic not in self.topic_subscriptions:
                return 0
            
            connections = self.topic_subscriptions[topic].copy()
            sent_count = 0
            
            for connection_id in connections:
                success = await self.send_personal_message(message, connection_id)
                if success:
                    sent_count += 1
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending topic message to topic {topic}: {str(e)}")
            return 0
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all active connections"""
        try:
            connections = list(self.active_connections.keys())
            sent_count = 0
            
            for connection_id in connections:
                success = await self.send_personal_message(message, connection_id)
                if success:
                    sent_count += 1
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
            return 0
    
    def subscribe_to_topic(self, connection_id: str, topic: str):
        """Subscribe a connection to a topic"""
        try:
            if topic not in self.topic_subscriptions:
                self.topic_subscriptions[topic] = []
            
            if connection_id not in self.topic_subscriptions[topic]:
                self.topic_subscriptions[topic].append(connection_id)
            
            logger.info(f"Connection {connection_id} subscribed to topic {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to topic {topic}: {str(e)}")
            return False
    
    def unsubscribe_from_topic(self, connection_id: str, topic: str):
        """Unsubscribe a connection from a topic"""
        try:
            if topic in self.topic_subscriptions:
                if connection_id in self.topic_subscriptions[topic]:
                    self.topic_subscriptions[topic].remove(connection_id)
                
                # Clean up empty topic
                if not self.topic_subscriptions[topic]:
                    del self.topic_subscriptions[topic]
            
            logger.info(f"Connection {connection_id} unsubscribed from topic {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing from topic {topic}: {str(e)}")
            return False
    
    async def handle_message(
        self,
        message: Dict[str, Any],
        connection_id: str,
        user: CurrentUser
    ):
        """Handle incoming WebSocket message"""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type == "ping":
                await self.send_personal_message({
                    "type": "pong",
                    "data": {"timestamp": datetime.utcnow().isoformat()}
                }, connection_id)
            
            elif message_type == "subscribe":
                topic = data.get("topic")
                if topic:
                    success = self.subscribe_to_topic(connection_id, topic)
                    await self.send_personal_message({
                        "type": "subscription_result",
                        "data": {"topic": topic, "success": success}
                    }, connection_id)
            
            elif message_type == "unsubscribe":
                topic = data.get("topic")
                if topic:
                    success = self.unsubscribe_from_topic(connection_id, topic)
                    await self.send_personal_message({
                        "type": "unsubscription_result",
                        "data": {"topic": topic, "success": success}
                    }, connection_id)
            
            elif message_type == "send_message":
                # Handle chat message
                await self._handle_chat_message(data, user, connection_id)
            
            elif message_type == "typing_indicator":
                # Handle typing indicator
                await self._handle_typing_indicator(data, user, connection_id)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
    
    async def _handle_chat_message(
        self,
        data: Dict[str, Any],
        user: CurrentUser,
        connection_id: str
    ):
        """Handle chat message"""
        try:
            recipient_ids = data.get("recipient_ids", [])
            content = data.get("content", "")
            thread_id = data.get("thread_id")
            
            if not recipient_ids or not content:
                return
            
            # Create real-time message
            message = {
                "type": "new_message",
                "data": {
                    "message_id": str(uuid.uuid4()),
                    "sender_id": user.user_id,
                    "sender_name": user.full_name,
                    "content": content,
                    "thread_id": thread_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Send to recipients
            for recipient_id in recipient_ids:
                await self.send_user_message(message, recipient_id)
            
        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")
    
    async def _handle_typing_indicator(
        self,
        data: Dict[str, Any],
        user: CurrentUser,
        connection_id: str
    ):
        """Handle typing indicator"""
        try:
            thread_id = data.get("thread_id")
            is_typing = data.get("is_typing", False)
            
            if not thread_id:
                return
            
            # Send typing indicator to thread topic
            message = {
                "type": "typing_indicator",
                "data": {
                    "user_id": user.user_id,
                    "user_name": user.full_name,
                    "thread_id": thread_id,
                    "is_typing": is_typing,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await self.send_topic_message(message, f"thread_{thread_id}")
            
        except Exception as e:
            logger.error(f"Error handling typing indicator: {str(e)}")
    
    async def _remove_broken_connection(self, connection_id: str):
        """Remove a broken connection"""
        try:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            
            # Remove from user connections
            for user_id, connections in self.user_connections.items():
                if connection_id in connections:
                    connections.remove(connection_id)
            
            # Remove from school connections
            for school_id, connections in self.school_connections.items():
                if connection_id in connections:
                    connections.remove(connection_id)
            
            # Remove from topic subscriptions
            for topic, connections in self.topic_subscriptions.items():
                if connection_id in connections:
                    connections.remove(connection_id)
            
            logger.info(f"Removed broken connection {connection_id}")
            
        except Exception as e:
            logger.error(f"Error removing broken connection: {str(e)}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "users_online": len(self.user_connections),
            "schools_active": len(self.school_connections),
            "active_topics": len(self.topic_subscriptions),
            "topics": list(self.topic_subscriptions.keys())
        }

# Global connection manager instance
connection_manager = ConnectionManager()

class EventBroadcaster:
    """Handles broadcasting of real-time events"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def broadcast_event(self, event: RealTimeEvent):
        """Broadcast a real-time event"""
        try:
            message = {
                "type": "real_time_event",
                "data": {
                    "event_type": event.event_type,
                    "data": event.data,
                    "user_id": event.user_id,
                    "school_id": event.school_id,
                    "timestamp": event.timestamp.isoformat()
                }
            }
            
            # Broadcast to school
            await self.connection_manager.send_school_message(message, event.school_id)
            
        except Exception as e:
            logger.error(f"Error broadcasting event: {str(e)}")
    
    async def send_user_notification(self, user_id: int, notification: Dict[str, Any]):
        """Send notification to a specific user"""
        try:
            message = {
                "type": "notification",
                "data": notification
            }
            
            await self.connection_manager.send_user_message(message, user_id)
            
        except Exception as e:
            logger.error(f"Error sending user notification: {str(e)}")
    
    async def send_system_announcement(self, school_id: int, announcement: Dict[str, Any]):
        """Send system announcement to a school"""
        try:
            message = {
                "type": "system_announcement",
                "data": announcement
            }
            
            await self.connection_manager.send_school_message(message, school_id)
            
        except Exception as e:
            logger.error(f"Error sending system announcement: {str(e)}")

# Global event broadcaster instance
event_broadcaster = EventBroadcaster(connection_manager)
