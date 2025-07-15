"""
WebSocket handler for EduNerve API Gateway
Handles real-time communication and message routing
"""

import json
import logging
import asyncio
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self):
        # Store active connections
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Map users to their connections
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Map rooms to users
        self.room_users: Dict[str, Set[str]] = {}
        
        # Store user information
        self.user_info: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Store connection
        self.active_connections[connection_id] = websocket
        
        # Map user to connection
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        logger.info(f"User {user_id} connected with connection {connection_id}")
        
        # Send connection confirmation
        await self.send_personal_message(user_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, user_id: str, connection_id: str):
        """Disconnect a WebSocket connection"""
        # Remove connection
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove user mapping
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from all rooms
        for room_id in list(self.room_users.keys()):
            if user_id in self.room_users[room_id]:
                self.room_users[room_id].discard(user_id)
                if not self.room_users[room_id]:
                    del self.room_users[room_id]
        
        # Remove user info
        if user_id in self.user_info:
            del self.user_info[user_id]
        
        logger.info(f"User {user_id} disconnected connection {connection_id}")
    
    async def send_personal_message(self, user_id: str, message: Dict):
        """Send a message to a specific user"""
        if user_id in self.user_connections:
            # Convert message to JSON
            message_str = json.dumps(message)
            
            # Send to all user's connections
            for connection_id in self.user_connections[user_id].copy():
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_text(message_str)
                    except Exception as e:
                        logger.error(f"Failed to send message to {user_id}: {e}")
                        self.disconnect(user_id, connection_id)
    
    async def send_room_message(self, room_id: str, message: Dict, exclude_user: Optional[str] = None):
        """Send a message to all users in a room"""
        if room_id in self.room_users:
            for user_id in self.room_users[room_id]:
                if user_id != exclude_user:
                    await self.send_personal_message(user_id, message)
    
    async def broadcast_message(self, message: Dict):
        """Send a message to all connected users"""
        message_str = json.dumps(message)
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
    
    def join_room(self, user_id: str, room_id: str):
        """Add a user to a room"""
        if room_id not in self.room_users:
            self.room_users[room_id] = set()
        self.room_users[room_id].add(user_id)
        
        logger.info(f"User {user_id} joined room {room_id}")
    
    def leave_room(self, user_id: str, room_id: str):
        """Remove a user from a room"""
        if room_id in self.room_users:
            self.room_users[room_id].discard(user_id)
            if not self.room_users[room_id]:
                del self.room_users[room_id]
        
        logger.info(f"User {user_id} left room {room_id}")
    
    def get_room_users(self, room_id: str) -> Set[str]:
        """Get all users in a room"""
        return self.room_users.get(room_id, set())
    
    def get_user_rooms(self, user_id: str) -> Set[str]:
        """Get all rooms a user is in"""
        rooms = set()
        for room_id, users in self.room_users.items():
            if user_id in users:
                rooms.add(room_id)
        return rooms
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is online"""
        return user_id in self.user_connections
    
    def get_online_users(self) -> Set[str]:
        """Get all online users"""
        return set(self.user_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_user_count(self) -> int:
        """Get total number of connected users"""
        return len(self.user_connections)

class MessageHandler:
    """Handles different types of WebSocket messages"""
    
    def __init__(self, ws_manager: WebSocketManager, service_urls: Dict[str, str]):
        self.ws_manager = ws_manager
        self.service_urls = service_urls
    
    async def handle_message(self, user_id: str, message: Dict):
        """Route message to appropriate handler"""
        message_type = message.get("type")
        
        if message_type == "chat":
            await self.handle_chat_message(user_id, message)
        elif message_type == "join_room":
            await self.handle_join_room(user_id, message)
        elif message_type == "leave_room":
            await self.handle_leave_room(user_id, message)
        elif message_type == "typing":
            await self.handle_typing_indicator(user_id, message)
        elif message_type == "presence":
            await self.handle_presence_update(user_id, message)
        elif message_type == "file_share":
            await self.handle_file_share(user_id, message)
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def handle_chat_message(self, user_id: str, message: Dict):
        """Handle chat messages"""
        try:
            # Forward to sync service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.service_urls['sync']}/api/v1/sync/messages",
                    json={
                        "user_id": user_id,
                        "content": message.get("content"),
                        "conversation_id": message.get("conversation_id"),
                        "message_type": message.get("message_type", "text")
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    # Get the saved message
                    saved_message = response.json()
                    
                    # Send to room participants
                    conversation_id = message.get("conversation_id")
                    if conversation_id:
                        await self.ws_manager.send_room_message(
                            f"conversation_{conversation_id}",
                            {
                                "type": "message_received",
                                "message": saved_message,
                                "timestamp": datetime.now().isoformat()
                            },
                            exclude_user=user_id
                        )
                    
                    # Send confirmation to sender
                    await self.ws_manager.send_personal_message(user_id, {
                        "type": "message_sent",
                        "message": saved_message,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    await self.ws_manager.send_personal_message(user_id, {
                        "type": "error",
                        "message": "Failed to send message",
                        "timestamp": datetime.now().isoformat()
                    })
        
        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            await self.ws_manager.send_personal_message(user_id, {
                "type": "error",
                "message": "Message sending failed",
                "timestamp": datetime.now().isoformat()
            })
    
    async def handle_join_room(self, user_id: str, message: Dict):
        """Handle room join requests"""
        room_id = message.get("room_id")
        if room_id:
            self.ws_manager.join_room(user_id, room_id)
            
            # Notify other users in the room
            await self.ws_manager.send_room_message(
                room_id,
                {
                    "type": "user_joined",
                    "user_id": user_id,
                    "room_id": room_id,
                    "timestamp": datetime.now().isoformat()
                },
                exclude_user=user_id
            )
            
            # Send confirmation to user
            await self.ws_manager.send_personal_message(user_id, {
                "type": "room_joined",
                "room_id": room_id,
                "users": list(self.ws_manager.get_room_users(room_id)),
                "timestamp": datetime.now().isoformat()
            })
    
    async def handle_leave_room(self, user_id: str, message: Dict):
        """Handle room leave requests"""
        room_id = message.get("room_id")
        if room_id:
            # Notify other users in the room
            await self.ws_manager.send_room_message(
                room_id,
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "room_id": room_id,
                    "timestamp": datetime.now().isoformat()
                },
                exclude_user=user_id
            )
            
            self.ws_manager.leave_room(user_id, room_id)
            
            # Send confirmation to user
            await self.ws_manager.send_personal_message(user_id, {
                "type": "room_left",
                "room_id": room_id,
                "timestamp": datetime.now().isoformat()
            })
    
    async def handle_typing_indicator(self, user_id: str, message: Dict):
        """Handle typing indicators"""
        room_id = message.get("room_id")
        is_typing = message.get("is_typing", False)
        
        if room_id:
            await self.ws_manager.send_room_message(
                room_id,
                {
                    "type": "typing_indicator",
                    "user_id": user_id,
                    "is_typing": is_typing,
                    "timestamp": datetime.now().isoformat()
                },
                exclude_user=user_id
            )
    
    async def handle_presence_update(self, user_id: str, message: Dict):
        """Handle presence updates"""
        status = message.get("status", "online")
        
        # Update user presence in all rooms
        for room_id in self.ws_manager.get_user_rooms(user_id):
            await self.ws_manager.send_room_message(
                room_id,
                {
                    "type": "presence_update",
                    "user_id": user_id,
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                },
                exclude_user=user_id
            )
    
    async def handle_file_share(self, user_id: str, message: Dict):
        """Handle file sharing notifications"""
        room_id = message.get("room_id")
        file_info = message.get("file_info", {})
        
        if room_id and file_info:
            await self.ws_manager.send_room_message(
                room_id,
                {
                    "type": "file_shared",
                    "user_id": user_id,
                    "file_info": file_info,
                    "timestamp": datetime.now().isoformat()
                },
                exclude_user=user_id
            )

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
