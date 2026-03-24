import json
from typing import Any, Awaitable, Callable

from redis.asyncio import Redis

from app.core.config import settings


async def get_or_set_cache(
    redis: Redis,
    key: str,
    fallback: Callable[[], Awaitable[Any]],
    ttl: int | None = None,
) -> Any:
    cached = await redis.get(key)
    if cached is not None:
        return json.loads(cached)
    data = await fallback()
    await redis.setex(key, ttl or settings.REQUEST_CACHE_TTL_SECONDS, json.dumps(data, default=str))
    return data
