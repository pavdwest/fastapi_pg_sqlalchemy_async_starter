from typing import Dict

from fastapi import APIRouter, status


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
async def home(
    ) -> Dict:
    """
    Home

    Args:
        response (Response): Ignore, it's for internal use.

    Returns:
        Dict: {
            'message': 'Hello boils and ghouls'
        }
    """
    return {
        'message': 'Hello boils and ghouls'
    }
