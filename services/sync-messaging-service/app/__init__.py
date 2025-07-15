"""EduNerve Sync & Messaging Service Package"""

__version__ = "1.0.0"
__author__ = "EduNerve Team"
__description__ = "Offline synchronization, messaging, notifications, and real-time communication service"

from .main import app
from .sync_messaging_service import sync_messaging_service
from .websocket_manager import connection_manager, event_broadcaster

__all__ = [
    "app",
    "sync_messaging_service", 
    "connection_manager",
    "event_broadcaster"
]
