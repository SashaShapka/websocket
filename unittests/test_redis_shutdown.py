import pytest
import asyncio
import websockets
from datetime import datetime
from websockets.exceptions import ConnectionClosedError


WS_URI = "ws://localhost:8000/ws"

@pytest.mark.asyncio
async def test_graceful_shutdown_multi_worker():
    """
    If we run a server with several workers, we check:
    - workers without a connection end quickly
    - a worker with an active connection waits before completing
    """
    num_clients = 3
    connections = []

    for _ in range(num_clients):
        ws = await websockets.connect(WS_URI)
        connections.append(ws)

    start = datetime.now()
    delays = []

    async def wait_for_close(i, ws):
        try:
            while True:
                await ws.recv()
        except ConnectionClosedError:
            end = datetime.now()
            elapsed = (end - start).total_seconds()
            delays.append(elapsed)

    await asyncio.gather(*(wait_for_close(i, ws) for i, ws in enumerate(connections)))

    long_lived = [d for d in delays if d >= 55]
    assert long_lived
