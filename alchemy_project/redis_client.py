import os
from typing import Optional

import redis.asyncio as redis


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> Optional[redis.Redis]:
    """Получает или создаёт Redis клиент"""
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Проверяем подключение
            await _redis_client.ping()
            print("Redis подключен успешно")
        except Exception as e:
            print(f"Не удалось подключиться к Redis: {e}")
            _redis_client = None

    return _redis_client


async def close_redis():
    """Закрывает соединение с Redis"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        print("Redis соединение закрыто")