import os
from redis.asyncio import Redis
redis = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT",6379)), decode_responses=True)