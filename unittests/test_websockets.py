import asyncio
import websockets
from datetime import datetime
import pytest

WS_URI = "ws://localhost:8000/ws"

@pytest.mark.asyncio
async def test_case_1_delayed_message():
    """The client sends nothing and receives two messages ~10 seconds apart."""
    async with websockets.connect(WS_URI) as ws:
        start_1 = datetime.now()
        message_1 = await ws.recv()
        elapsed_1 = (datetime.now() - start_1).total_seconds()

        assert "broadcast" in message_1.lower()
        assert 9 <= elapsed_1 <= 12

        start_2 = datetime.now()
        message_2 = await ws.recv()
        elapsed_2 = (datetime.now() - start_2).total_seconds()

        assert "broadcast" in message_2.lower()
        assert 9 <= elapsed_2 <= 12


@pytest.mark.asyncio
async def test_case_2_immediate_response():
    """Client sends 'send_now' and gets response immediately."""
    async with websockets.connect(WS_URI) as ws:
        await asyncio.sleep(1)
        await ws.send("send_now")
        start = datetime.now()
        message = await ws.recv()
        elapsed = (datetime.now() - start).total_seconds()

        assert "immediate" in message.lower()
        assert elapsed < 2


@pytest.mark.asyncio
async def test_case_3_multiple_clients():
    """Three clients, one of which sends 'send_now'."""
    results = {}

    async def client(name, send_now=False):
        async with websockets.connect(WS_URI) as ws:
            if send_now:
                await asyncio.sleep(1)
                await ws.send("send_now")
                start = datetime.now()
                message = await ws.recv()
                elapsed = (datetime.now() - start).total_seconds()
                results[name] = (message, elapsed)
            else:
                start = datetime.now()
                message = await ws.recv()
                elapsed = (datetime.now() - start).total_seconds()
                results[name] = (message, elapsed)

    await asyncio.gather(
        client("Client A", send_now=True),
        client("Client B"),
        client("Client C")
    )

    assert "immediate" in results["Client A"][0].lower()
    assert results["Client A"][1] < 2

    for name in ["Client B", "Client C"]:
        assert "broadcast" in results[name][0].lower()
        assert 9 <= results[name][1] <= 12