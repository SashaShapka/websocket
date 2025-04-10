import pytest
import websockets
from datetime import datetime
from websockets.exceptions import ConnectionClosedError

WS_URI = "ws://localhost:8000/ws"

@pytest.mark.asyncio
async def test_shutdown_waits_for_client_disconnect():
    """
        The client opens the connection and keeps it open.
        After manually terminating the server (SIGINT), the connection should last ~60 seconds.
    """

    async with websockets.connect(WS_URI) as ws:
        start = datetime.now()

        try:
            while True:
                await ws.recv()
        except ConnectionClosedError as e:
            end = datetime.now()
            elapsed = (end - start).total_seconds()
            assert elapsed >= 55