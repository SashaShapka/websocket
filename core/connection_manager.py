from typing import Dict
from fastapi import WebSocket
from datetime import datetime, timedelta
import logging
from core.singeltone import Singleton

logger = logging.getLogger('socket_logger')

class ConnectionManager(metaclass=Singleton):
    """
        A connection manager that tracks new connections and implements methods for checking the connection status
    """

    def __init__(self):
        self.active_connections: Dict[WebSocket, datetime] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = datetime.utcnow() + timedelta(seconds=10)

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.pop(websocket, None)

    def has_connections(self) -> bool:
        return bool(self.active_connections)


    def get_connections(self) -> Dict[WebSocket, datetime]:
        return self.active_connections

