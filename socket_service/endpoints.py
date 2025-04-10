import os

from fastapi import  WebSocket, WebSocketDisconnect
from core.connection_manager import ConnectionManager
from core.broadcast_strategy import context
import logging

logger = logging.getLogger('socket_logger')

async def websocket_endpoint(websocket: WebSocket):
    await ConnectionManager().connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            if data == "send_now":
                context.mark_recent(websocket)
                logger.info(f"{os.getpid()} Send message immediately")
                await websocket.send_text("Immediate message sent")


            elif data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        await ConnectionManager().disconnect(websocket)