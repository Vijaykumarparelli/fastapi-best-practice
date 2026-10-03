from datetime import datetime, timezone

from redis.asyncio import Redis

from config.settings import settings

_token_black = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


async def token_blacklist(jti: str, exp: int):
    now = int(datetime.now(timezone.utc).timestamp())
    ttl = exp - now
    if ttl > 0:
        await _token_black.set(
            str(jti),
            "blocked",
            ex=ttl,
        )


async def is_token_blacklist(
    jti: str,
) -> bool:
    return await _token_black.exists(jti)
