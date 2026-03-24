import hashlib
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, Request, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.models.api_key import ApiKey

_rate_bucket: dict[str, deque[datetime]] = defaultdict(deque)


def hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


async def get_redis() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def verify_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    api_key: str | None = Header(default=None, alias=settings.API_KEY_HEADER),
) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == hash_key(api_key), ApiKey.is_active.is_(True))
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


async def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=1)
    bucket = _rate_bucket[ip]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    bucket.append(now)
