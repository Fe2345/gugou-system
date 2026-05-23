import redis
from django.conf import settings

_client = None


def _redis():
    global _client
    if _client is None:
        _client = redis.Redis(
            host=settings.REDIS_HOST,
            port=int(settings.REDIS_PORT),
            db=1,
            decode_responses=True,
        )
    return _client


def next_seq(key: str) -> int:
    """Redis INCR 原子递增，返回唯一序号。key 建议带日期以每日重置。"""
    return _redis().incr(key)
