import asyncio
from typing import Dict

from fastapi import APIRouter, status, Response

from src.logging.service import logger
from src.versions import ApiVersion
from src.modules.arqueue.bus import Bus


router = APIRouter(
    tags=['Arqueue'],
)


@router.get(
    '/arqueue/sandbox',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary='Sandbox for testing Arqueue',
    description='Endpoint description. Will use the docstring if not provided.',
)
async def sandbox(response: Response) -> Dict:
    urls = [
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
        'https://catfact.ninja/fact',
    ]
    tasks = [Bus.queue.enqueue_job('download_content', url) for url in urls]
    await asyncio.gather(*tasks)

    return {
        'message': 'Sandbox tasks enqueued.',
    }


@router.get(
    '/arqueue/throughput',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary='Throughput testing Arqueue',
    description='Endpoint description. Will use the docstring if not provided.',
)
async def no_op_task(response: Response) -> Dict:

    n = 10000

    # Blast
    # 11s for 5k with 1 worker - 450/s, very slow too
    # 6s for 5k with 20 worker - 900/s, very slow too
    # tasks = [Bus.queue.enqueue_job('no_op_task', i) for i in range(n)]
    # await asyncio.gather(*tasks)

    # Iterate
    # 25s for 10k with 1 worker: 400/s, very slow
    # 6s for 5k with 20 worker: 900/s, very slow too
    # 125s for 50k with 2 worker: 400/s, very slow too
    # 48 for 50k with 20 worker: 1000/s, very slow too
    logger.warning(f'Enqueuing {n} tasks...')
    for i in range(n):
        await Bus.queue.enqueue_job('no_op_task', i)
    logger.warning(f'Enqueued {n} tasks')

    return {
        'message': 'Sandbox tasks enqueued.',
    }
