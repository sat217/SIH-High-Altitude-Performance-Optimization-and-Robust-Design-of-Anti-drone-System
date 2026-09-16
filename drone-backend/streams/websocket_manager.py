"""
WebSocket manager for real-time communication with frontend
"""
import json
import asyncio
import base64
import cv2
import numpy as np
from typing import Dict, Set, Optional
from fastapi import WebSocket
import logging

logger = logging.getLogger(__file__)


class WebSocketManager:
    """Manages WebSocket connections for real-time streaming"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
        
        # Send initial status
        await self.send_json(websocket, {
            'type': 'status',
            'message': 'Connected to SKY SENTINEL Backend',
            'mode': 'normal'
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_frame(
        self, 
        frame: np.ndarray, 
        detections: list = None, 
        mode: str = 'normal',
        active_alert: Optional[dict] = None  # ✅ NEW: Embed alert in frame
    ):
        """
        Send processed frame to all connected clients
        
        Args:
            frame: Processed BGR image
            detections: List of detection dictionaries
            mode: Current processing mode ('normal' or 'thermal')
            active_alert: Optional alert payload to embed in frame message
        """
        if not self.active_connections:
            return
        
        try:
            # Encode frame to JPEG
            _, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_base64 = base64.b64encode(encoded).decode('utf-8')
            
            # Prepare message WITH embedded alert
            message = {
                'type': 'frame',
                'frame': frame_base64,
                'detections': detections or [],
                'mode': mode,
                'timestamp': asyncio.get_event_loop().time(),
                'alert': active_alert  # ✅ Alert travels INSIDE frame message
            }
            
            # Send to all connected clients
            disconnected = set()
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    disconnected.add(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn)
                
        except Exception as e:
            logger.error(f"Error encoding/sending frame: {e}")
    
    async def send_json(self, websocket: WebSocket, data: dict):
        """Send JSON message to specific client"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Error sending JSON: {e}")
            self.disconnect(websocket)
    
    # ❌ REMOVED: broadcast_alert() - No longer needed since alerts are embedded