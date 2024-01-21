from typing import Dict

from fastapi import APIRouter, status, Response

from src.versions import ApiVersion


router = APIRouter(
    tags=['Admin'],
    prefix=f"{ApiVersion.V1}/admin",
)


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    summary='Returns 200 if service is up and running',
    description='Endpoint description. Will use the docstring if not provided.',
)
async def test(response: Response) -> Dict:
    """
    Home

    Args:
        response (Response): Ignore, it's for internal use.

    Returns:
        Dict: {
            'message': 'Hello boils and ghouls'
        }
    """
    response.status_code = status.HTTP_200_OK
    return {
        'message': 'Admin Test'
    }
