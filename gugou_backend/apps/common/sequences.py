import os
import threading
from pathlib import Path

from django.conf import settings

_client = None
_lock = threading.Lock()
_seq_file = Path(settings.BASE_DIR) / ".seq_cache"


def _get_file_seq(key: str) -> int:
    """文件备用方案，当 Redis 不可用时使用"""
    with _lock:
        data = {}
        if _seq_file.exists():
            with open(_seq_file, "r") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        try:
                            data[k] = int(v)
                        except ValueError:
                            pass

        seq = data.get(key, 0) + 1
        data[key] = seq

        with open(_seq_file, "w") as f:
            for k, v in data.items():
                f.write(f"{k}={v}\n")

        return seq


def next_seq(key: str) -> int:
    """原子递增序号。优先使用 Redis，不可用时回退到文件。"""
    try:
        import redis
        global _client
        if _client is None:
            _client = redis.Redis(
                host=settings.REDIS_HOST,
                port=int(settings.REDIS_PORT),
                db=1,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
        return _client.incr(key)
    except Exception:
        return _get_file_seq(key)
