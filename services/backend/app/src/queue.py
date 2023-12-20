import asyncio
from httpx import AsyncClient
from arq import create_pool
from arq.connections import RedisSettings

import src.config as config
from src.logging.service import logger


async def queue_init():
    logger.info('Creating Redis pool...')
    redis = await create_pool(
        RedisSettings(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD,
        )
    )

    if not await redis.ping():
        raise Exception('Redis is not available')

    return redis
