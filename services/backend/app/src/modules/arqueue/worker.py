from httpx import AsyncClient

from arq.connections import RedisSettings

from src.logging.service import logger
import src.config as config


async def download_content(ctx, url):
    logger.info(f'Starting task for {url}...')
    # session: AsyncClient = ctx['session']
    # response = await session.get(url)
    # print(f'{url}: {response.text:.80}...')
    # return len(response.text)
    return len(url)

async def startup(ctx):
    logger.info('Starting up...')
    ctx['session'] = AsyncClient()
    logger.info('Startup complete')

async def shutdown(ctx):
    await ctx['session'].aclose()


# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings, see https://arq-docs.helpmanual.io/#arq.worker.Worker
class WorkerSettings:
    functions = [download_content]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings=RedisSettings(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
    )
