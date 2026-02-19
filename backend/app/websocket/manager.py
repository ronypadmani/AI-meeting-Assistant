"""
WebSocket manager for real-time communication
"""
import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from ..models.schemas import (
    WebSocketMessage, StatusMessage, ConnectionMessage, 
    ChunkUpdate, SummaryUpdate, HeartbeatMessage
)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Active connections: {client_id: connection_info}
        self.active_connections: Dict[str, Dict] = {}
        # Session subscriptions: {session_id: set of client_ids}
        self.session_subscriptions: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Generate client ID if not provided
        if not client_id:
            client_id = str(uuid.uuid4())
        
        # Store connection info
        connection_info = {
            "websocket": websocket,
            "client_id": client_id,
            "connected_at": datetime.utcnow(),
            "subscribed_sessions": set(),
            "last_heartbeat": datetime.utcnow()
        }
        
        self.active_connections[client_id] = connection_info
        
        # Send connection confirmation
        connection_msg = ConnectionMessage(
            status="connected",
            client_id=client_id
        )
        
        await self._send_to_client(client_id, connection_msg.dict())
        
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        return client_id
    
    def disconnect(self, client_id: str):
        """Remove a client connection"""
        if client_id in self.active_connections:
            connection_info = self.active_connections[client_id]
            
            # Remove from all session subscriptions
            subscribed_sessions = connection_info["subscribed_sessions"].copy()
            for session_id in subscribed_sessions:
                self.unsubscribe_from_session(client_id, session_id)
            
            # Remove from active connections
            del self.active_connections[client_id]
            
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    def subscribe_to_session(self, client_id: str, session_id: str):
        """Subscribe a client to session updates"""
        if client_id in self.active_connections:
            # Add to client's subscriptions
            self.active_connections[client_id]["subscribed_sessions"].add(session_id)
            
            # Add to session subscriptions
            if session_id not in self.session_subscriptions:
                self.session_subscriptions[session_id] = set()
            self.session_subscriptions[session_id].add(client_id)
            
            logger.info(f"Client {client_id} subscribed to session {session_id}")
    
    def unsubscribe_from_session(self, client_id: str, session_id: str):
        """Unsubscribe a client from session updates"""
        if client_id in self.active_connections:
            self.active_connections[client_id]["subscribed_sessions"].discard(session_id)
        
        if session_id in self.session_subscriptions:
            self.session_subscriptions[session_id].discard(client_id)
            
            # Clean up empty session subscriptions
            if not self.session_subscriptions[session_id]:
                del self.session_subscriptions[session_id]
        
        logger.info(f"Client {client_id} unsubscribed from session {session_id}")
    
    async def _send_to_client(self, client_id: str, message: Dict) -> bool:
        """Send message to a specific client"""
        if client_id not in self.active_connections:
            return False
        
        websocket = self.active_connections[client_id]["websocket"]
        
        try:
            await websocket.send_text(json.dumps(message, default=str))
            return True
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {e}")
            # Remove disconnected client
            self.disconnect(client_id)
            return False
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        disconnected_clients = []
        
        for client_id in self.active_connections:
            success = await self._send_to_client(client_id, message)
            if not success:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_to_session(self, session_id: str, message: Dict):
        """Broadcast message to all clients subscribed to a session"""
        if session_id not in self.session_subscriptions:
            return
        
        client_ids = self.session_subscriptions[session_id].copy()
        disconnected_clients = []
        
        for client_id in client_ids:
            success = await self._send_to_client(client_id, message)
            if not success:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_chunk_update(self, session_id: str, chunk_data: Dict):
        """Send chunk update to session subscribers"""
        chunk_update = ChunkUpdate(
            session_id=session_id,
            chunk=chunk_data
        )
        
        await self.broadcast_to_session(session_id, chunk_update.dict())
        logger.info(f"Sent chunk update for session {session_id} to {len(self.session_subscriptions.get(session_id, []))} clients")
    
    async def send_summary_update(self, session_id: str, summary_data: Dict):
        """Send summary update to session subscribers"""
        summary_update = SummaryUpdate(
            session_id=session_id,
            summary=summary_data
        )
        
        await self.broadcast_to_session(session_id, summary_update.dict())
        logger.info(f"Sent summary update for session {session_id} to {len(self.session_subscriptions.get(session_id, []))} clients")
    
    async def send_status_update(self, session_id: Optional[str], status: str, details: Optional[Dict] = None):
        """Send status update"""
        status_msg = StatusMessage(
            session_id=session_id,
            status=status,
            details=details
        )
        
        if session_id:
            await self.broadcast_to_session(session_id, status_msg.dict())
        else:
            await self.broadcast_to_all(status_msg.dict())
    
    async def handle_client_message(self, client_id: str, message: Dict):
        """Handle incoming message from client"""
        try:
            message_type = message.get("type")
            
            if message_type == "subscribe":
                session_id = message.get("session_id")
                if session_id:
                    self.subscribe_to_session(client_id, session_id)
                    await self._send_to_client(client_id, {
                        "type": "subscription_confirmed",
                        "session_id": session_id,
                        "status": "subscribed"
                    })
            
            elif message_type == "unsubscribe":
                session_id = message.get("session_id")
                if session_id:
                    self.unsubscribe_from_session(client_id, session_id)
                    await self._send_to_client(client_id, {
                        "type": "subscription_confirmed",
                        "session_id": session_id,
                        "status": "unsubscribed"
                    })
            
            elif message_type == "heartbeat":
                # Update last heartbeat time
                if client_id in self.active_connections:
                    self.active_connections[client_id]["last_heartbeat"] = datetime.utcnow()
                
                # Send heartbeat response
                heartbeat_response = HeartbeatMessage()
                await self._send_to_client(client_id, heartbeat_response.dict())
            
            elif message_type == "get_status":
                # Send current system status
                await self._send_to_client(client_id, {
                    "type": "status_response",
                    "active_connections": len(self.active_connections),
                    "active_sessions": len(self.session_subscriptions),
                    "client_subscriptions": len(self.active_connections[client_id]["subscribed_sessions"]) if client_id in self.active_connections else 0
                })
            
            else:
                logger.warning(f"Unknown message type from client {client_id}: {message_type}")
        
        except Exception as e:
            logger.error(f"Error handling message from client {client_id}: {e}")
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "active_sessions": len(self.session_subscriptions),
            "session_details": {
                session_id: len(clients) 
                for session_id, clients in self.session_subscriptions.items()
            }
        }
    
    async def cleanup_stale_connections(self, max_idle_minutes: int = 30):
        """Remove connections that haven't sent heartbeat in a while"""
        current_time = datetime.utcnow()
        stale_clients = []
        
        for client_id, connection_info in self.active_connections.items():
            idle_time = (current_time - connection_info["last_heartbeat"]).total_seconds() / 60
            
            if idle_time > max_idle_minutes:
                stale_clients.append(client_id)
        
        for client_id in stale_clients:
            logger.info(f"Removing stale connection: {client_id}")
            self.disconnect(client_id)
        
        if stale_clients:
            logger.info(f"Cleaned up {len(stale_clients)} stale connections")


# Global connection manager instance
connection_manager = ConnectionManager()


async def start_heartbeat_task():
    """Background task to send periodic heartbeats and cleanup stale connections"""
    while True:
        try:
            # Send heartbeat to all clients
            heartbeat_msg = HeartbeatMessage()
            await connection_manager.broadcast_to_all(heartbeat_msg.dict())
            
            # Cleanup stale connections
            await connection_manager.cleanup_stale_connections()
            
            # Wait for next heartbeat interval
            await asyncio.sleep(30)  # 30 seconds
            
        except Exception as e:
            logger.error(f"Error in heartbeat task: {e}")
            await asyncio.sleep(5)  # Short wait before retry