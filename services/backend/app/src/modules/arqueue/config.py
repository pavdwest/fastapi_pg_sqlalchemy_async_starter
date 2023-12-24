from arq.connections import RedisSettings

from src import config


REDIS_SETTINGS=RedisSettings(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    database=1,
)
