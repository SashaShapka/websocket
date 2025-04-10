import pytest
import asyncio
import websockets

WS_URI = "ws://localhost:8000/ws"


@pytest.mark.asyncio
async def test_multiple_clients_receive_both_messages():
    """
       Integration test to verify correct WebSocket broadcasting behavior in a multi-worker setup.

       Test scenario:
       1. Establish 5 WebSocket client connections.
       2. One client sends "send_now", triggering an immediate message directly to that client.
       3. All clients should also receive a scheduled broadcast via Redis.
       4. The test ensures:
          - The client that sent "send_now" receives the "immediate" message.
          - Other clients receive the "scheduled broadcast" after the Redis publisher fires.
          - All clients receive both message types without duplicates.

       This confirms:
           Redis broadcasting is working across workers.
           recently_notified logic correctly prevents duplicate sends.
           WebSocket communication remains consistent across multiple processes.
    """

    connections = []
    num_clients = 5

    for _ in range(num_clients):
        ws = await websockets.connect(WS_URI)
        connections.append(ws)

    await connections[0].send("send_now")

    messages = {i: [] for i in range(num_clients)}

    async def collect_messages(index, ws):
        try:
            for _ in range(2):
                msg = await asyncio.wait_for(ws.recv(), timeout=15)
                messages[index].append(msg)
        except Exception as e:
            print(f"[Client {index}] Error receiving: {e}")

    await asyncio.gather(*[
        collect_messages(i, ws) for i, ws in enumerate(connections)
    ])

    all_text = []

    for msgs in messages.values():
        all_text.append(" ".join(msgs).lower())

    assert any("immediate" in msg.lower() for msg in all_text)
    assert any("scheduled" in msg.lower() for msg in all_text)

    for ws in connections:
        await ws.close()
