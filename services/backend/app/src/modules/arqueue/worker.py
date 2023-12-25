import random

from httpx import AsyncClient

from src.logging.service import logger
from src.modules.arqueue.config import REDIS_SETTINGS
from src.database.service import DatabaseService
from src.modules.book.models import Book

# Command line docker compose command to increase the number of workers:
# docker compose scale worker=10

async def download_content(ctx, url):
    logger.info(f'Starting task for {url}...')
    session: AsyncClient = ctx['session']
    response = await session.get(url)
    # print(f'{url}: {response.text:.80}...')
    return response.text

async def no_op_task(ctx, param):
    logger.info(f'Starting task for {param}...')
    # wait for 1 second
    # await asyncio.sleep(1)
    return f'Finished task for {param}'

async def db_task(ctx, param):
    logger.info(f'Starting task for {param}...')
    # res = await Book.read_by_id(param)
    # return f'Finished task for {res.name}'

    res = await Book.read_all(limit=10000)
    return f'Finished task for {res[random.randint(0, len(res) - 1)].name}'

async def startup(ctx):
    logger.info('Worker starting up...')
    ctx['session'] = AsyncClient()
    ctx['db'] = DatabaseService.get()
    logger.info('Worker startup complete')

async def shutdown(ctx):
    await ctx['session'].aclose()


# WorkerSettings defines the settings to use when creating the work,
# it's used by the arq cli.
# For a list of available settings, see https://arq-docs.helpmanual.io/#arq.worker.Worker
class ArqueueWorkerSettings:
    functions = [download_content, no_op_task, db_task]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings=REDIS_SETTINGS
    poll_delay=0.025
