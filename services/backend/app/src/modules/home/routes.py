from typing import Dict

from fastapi import APIRouter, status, Response

from src.versions import ApiVersion
from src.queue import queue_init


router = APIRouter(
    tags=['Home'],
)


@router.get(
    '/',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary='Returns 200 if service is up and running',
    description='Endpoint description. Will use the docstring if not provided.',
)
async def home(response: Response) -> Dict:
    """
    Home

    Args:
        response (Response): Ignore, it's for internal use.

    Returns:
        Dict: {
            'message': 'Hello boils and ghouls'
        }
    """
    queue = await queue_init()

    for url in ('https://facebook.com', 'https://microsoft.com', 'https://github.com'):
        await queue.enqueue_job('download_content', url)

    return {
        'message': 'Hello boils and ghouls'
    }
