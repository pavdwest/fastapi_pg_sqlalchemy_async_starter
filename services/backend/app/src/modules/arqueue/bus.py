from arq import create_pool, ArqRedis

from src.logging.service import logger
from src.modules.arqueue.config import REDIS_SETTINGS


class Bus:
    queue: ArqRedis = None

    @classmethod
    async def init(cls):
        logger.warning('Creating Redis pool...')
        cls.queue = await create_pool(REDIS_SETTINGS)
