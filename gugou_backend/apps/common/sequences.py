import os
import socket
import threading
import time
from pathlib import Path

from django.conf import settings

_client = None
_redis_disabled_until = 0
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
    use_redis = getattr(settings, "USE_REDIS", False)
    if not use_redis:
        return _get_file_seq(key)

    global _redis_disabled_until
    if time.monotonic() < _redis_disabled_until:
        return _get_file_seq(key)

    try:
        host = settings.REDIS_HOST
        port = int(settings.REDIS_PORT)
        with socket.create_connection((host, port), timeout=0.1):
            pass

        import redis
        global _client
        if _client is None:
            _client = redis.Redis(
                host=host,
                port=port,
                db=1,
                decode_responses=True,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
            )
        result = _client.incr(key)
        return result
    except Exception as e:
        import logging
        logging.getLogger("gugou").warning("Redis不可用，回退到文件序列: %s", e)
        _client = None
        _redis_disabled_until = time.monotonic() + 30
        return _get_file_seq(key)
