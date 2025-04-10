import asyncio
import logging
import os
import signal
from core.connection_manager import ConnectionManager

logger = logging.getLogger("socket_logger")

class GracefulShutdown:
    """
    1. Worker:
        A single process handles all connections
        ConnectionManager is a single in-memory object that knows exactly about all connections
        When received Ctrl+C (SIGINT), GracefulShutdown:
        sees active connections
        waits for them to close themselves (or timeout)
        completes the process
    2. Multi-workers:
        After SIGINT, all workers simultaneously:
        Checking their local WebSocket connections.
        If there is, they wait up to 60 seconds (checking every 5).
        If there are no connections → they are terminated immediately.
        Role of Redis:
        Defines the leader (one who follows active_clients:* and sends broadcast).
        But completion occurs independently for each worker, Redis does not decide when to "kill" the process.
        We don't use @app.on_event("shutdown"), because FastAPI will close the
        WebSocket connection first — and we need to wait before closing.
    """


    def __init__(self):
        self.manager = ConnectionManager()
        self.interval = int(os.getenv("INTERVAL", 5))
        self.timeout = int(os.getenv("TIMEOUT", 60))
        self.loop = asyncio.get_event_loop()
        self._register_signals()

    def _register_signals(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        logger.info(f"Signal {signum} received of {os.getpid()}. Evaluating shutdown...")
        self.loop.create_task(self._shutdown())

    async def _shutdown(self):
        logger.info("Graceful shutdown initiated")
        waited = 0

        while self.manager.has_connections() and waited < self.timeout:
            logger.info(
                f" Pid {os.getpid()} Waiting for connections to close... {len(self.manager.get_connections())} active")
            await asyncio.sleep(self.interval)
            waited += self.interval

        logger.info(f"[{os.getpid()}] No active clients or timeout reached. Shutting down.")
        os._exit(0)