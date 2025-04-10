import logging
import os
from abc import ABC, abstractmethod

from core.broadcast import broadcast
from core.redis_broadcaster import redis_broadcast

logger = logging.getLogger('socket_logger')

class Context:
    def __init__(self, workers_number):
        self.workers_number = workers_number
        self._strategy = self.mathc_url_to_strategy()

    def start(self):
        logger.info(f"Strategy selected: {self._strategy.__class__.__name__}")
        self._strategy.start_broadcaster()

    def mathc_url_to_strategy(self):
        if self.workers_number > 1:
            return RedisBroadcasterStrategy()
        else:
            return SingleBroadcasterStrategy()

    def call_broadcaster(self):
        logging.info(f"Set strategy {self._strategy}")
        error = self._strategy.start_broadcaster()
        return error

    def mark_recent(self, websocket):
        self._strategy.mark_recent(websocket)


class Strategy(ABC):
    """This is an abstraction class that describes an interface to strategies of
    RedisBroadcaster for multi-workers and of SingleBroadcaster for one-worker logic """

    @abstractmethod
    def start_broadcaster(self):
        pass

    @abstractmethod
    def mark_recent(self, websocket):
        pass


class RedisBroadcasterStrategy(Strategy):
    def start_broadcaster(self):
        redis_broadcast.start()

    def mark_recent(self, websocket):
        redis_broadcast.mark_recent(websocket)


class SingleBroadcasterStrategy(Strategy):
    def start_broadcaster(self):
        broadcast.start()

    def mark_recent(self, websocket):
        broadcast.mark_recent(websocket)


context = Context(workers_number=int(os.getenv("UVICORN_WORKERS", 1)))