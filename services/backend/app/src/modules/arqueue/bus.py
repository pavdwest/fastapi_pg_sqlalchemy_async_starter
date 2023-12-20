from arq import create_pool, ArqRedis
from arq.connections import RedisSettings

import src.config as config
from src.logging.service import logger


class Bus:
    queue: ArqRedis = None

    @classmethod
    async def init(cls):
        logger.warning('Creating Redis pool...')
        cls.queue = await create_pool(
            RedisSettings(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
            )
        )
