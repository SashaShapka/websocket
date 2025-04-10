import asyncio
import logging
import os
from typing import Set

from  redis_client import redis
from core.connection_manager import ConnectionManager

logger = logging.getLogger('socket_logger')


class RedisBroadcaster:
    """
        Redis to synchronize state and events between workers,
        because when you run FastAPI/Uvicorn with several workers (workers=3),
        each worker is a separate process with its own memory.
        They know nothing about each other without an additional intermediary.
        All workers listening to Redis support this event and
        send messages to their clients (except the one that has already received).
    """
    def __init__(self, channel_name="ws_broadcast"):
        self.channel = channel_name
        self._manager = ConnectionManager()
        self._recently_notified: Set = set()
        self._listen_task = None
        self._publish_task = None
        self._heartbeat_task = None

    def mark_recent(self, websocket):
        """
            An implementation of an interface to indicate a connection to which a response should be sent immediately
        """
        self._recently_notified.add(websocket)

    def start(self):
        if not self._listen_task:
            self._listen_task = asyncio.create_task(self.listen_and_broadcast())
        if not self._publish_task:
            self._publish_task = asyncio.create_task(self.publisher_loop())
        if not self._heartbeat_task:
            self._heartbeat_task = asyncio.create_task(self.heartbeat_loop())

    async def listen_and_broadcast(self):
        pubsub = redis.pubsub()
        await pubsub.subscribe(self.channel)

        async for msg in pubsub.listen():
            if msg["type"] == "message":
                logger.info(f"[{os.getpid()}] Received message from Redis: {msg['data']}")
                for ws in list(self._manager.get_connections()):
                    if ws in self._recently_notified:
                        logger.info(f"{os.getpid()}: Skipping recently notified client: {ws}")
                        continue
                    try:
                        await ws.send_text(msg["data"])
                        logger.info(f"[{os.getpid()}] Sent message to: {ws}")
                    except:
                        await self._manager.disconnect(ws)

                self._recently_notified.clear()

    async def publisher_loop(self):
        """
            We have a publisher_loop() (or broadcast_loop()) loop that:
            publishes a message to Redis once every X seconds → "Scheduled broadcast"
            all workers listen to Redis via pubsub.listen() and send messages to clients.
            If each worker publishes a message himself, then:
            each client will receive 3 identical messages
            Redis will be spammed
            mark_recent will not have time to process — we will get duplicates
        """

        lock_key = "broadcast_lock"
        lock_ttl = 15
        pid = os.getpid()
        i_am_leader = False

        while True:
            try:
                if not i_am_leader:
                    is_leader = await redis.set(lock_key, pid, ex=lock_ttl, nx=True)
                    if is_leader:
                        i_am_leader = True
                        logger.info(f"[{pid}] I'm the leader")
                    else:
                        logger.debug(f"[{pid}] Not a leader")

                if i_am_leader:
                    await redis.expire(lock_key, lock_ttl)

                    active_keys = await redis.keys("active_clients:*")
                    if active_keys:
                        await redis.publish(self.channel, "Scheduled broadcast")
                        logger.info(f"[{pid}] Published Scheduled broadcast")
                    else:
                        logger.info(f"[{pid}] No active clients. Skipping.")

            except Exception as e:
                logger.error(f"Failed to publish: {e}")
                i_am_leader = False

            await asyncio.sleep(10)


    async def heartbeat_loop(self):
        """
            If the keys are there, the leader decides that it's time to send the message
        """

        pid = os.getpid()
        key = f"active_clients:{pid}"

        while True:
            try:
                if self._manager.has_connections():
                    await redis.set(key, "1", ex=15)
                    logger.debug(f"[{pid}] Heartbeat: active clients")
                else:
                    await redis.delete(key)
                    logger.debug(f"[{pid}] No clients, heartbeat key removed")
            except Exception as e:
                logger.error(f"[{pid}] Heartbeat failed: {e}")

            await asyncio.sleep(5)


redis_broadcast = RedisBroadcaster()