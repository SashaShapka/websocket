import asyncio
import os
from datetime import datetime, timedelta

from core.connection_manager import ConnectionManager
from core.singeltone import Singleton
import logging


logger = logging.getLogger('socket_logger')


class Broadcaster(metaclass=Singleton):
    def __init__(self):
        self._manager = ConnectionManager()
        self._recently_notified = set()
        self._broadcast_task = None

    def mark_recent(self, websocket):
        """
            An implementation of an interface to indicate a connection to which a response should be sent immediately
        """
        self._recently_notified.add(websocket)

    def start(self):
        if self._broadcast_task is None:
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())

    async def _broadcast_loop(self):
        """ A broadcast loop that checks every second:
            - whether it is time for each WebSocket to receive a scheduled message by next message from conn manager.
            - if so — sends "Scheduled broadcast", updates the time of the next broadcast.
            - if the connection is broken — deletes it from the manager
        """
        while True:
            now = datetime.utcnow()

            for ws, next_time in list(self._manager.get_connections().items()):
                if now >= next_time:
                    try:
                        logger.info(f"[{os.getpid()}] Sent scheduled message to: {ws}")
                        await ws.send_text("Scheduled broadcast")
                        self._manager.active_connections[ws] = now + timedelta(seconds=10)
                    except:
                        await self._manager.disconnect(ws)

            await asyncio.sleep(1)

broadcast = Broadcaster()