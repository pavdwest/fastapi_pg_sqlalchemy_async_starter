from typing import Dict

from fastapi import APIRouter, status


router = APIRouter(
    tags=['Home'],
)


@router.get(
    '/',
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

    from src.modules.review.models import Review
    item = await Review.read_all(schema_name='tenant_82f02b5b_c3d3_48c9_a884_d26cfc5e423f')

    return {
        'message': 'Hello boils and ghouls'
    }
