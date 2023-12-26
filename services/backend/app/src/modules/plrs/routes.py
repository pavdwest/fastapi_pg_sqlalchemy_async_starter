from typing import Dict
import time

from fastapi import status
import polars as pl

from src.logging.service import logger
from src.config import DATABASE_URL
from src.database.service import DatabaseService
from src.modules.plrs.models import Trade
from src.modules.plrs.validators import (
    TradeCreate,
    TradeGet,
    TradeUpdate,
    TradeUpdateWithId
)
from src.routes import generate_route_class


RouteClass = generate_route_class(
    ModelClass                 = Trade,
    CreateValidatorClass       = TradeCreate,
    ReadValidatorClass         = TradeGet,
    UpdateValidatorClass       = TradeUpdate,
    UpdateWithIdValidatorClass = TradeUpdateWithId,
)
router = RouteClass()


@(router.router).get(
    'sandbox/',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary='Sandbox for testing Polars',
    description='Endpoint description. Will use the docstring if not provided.',
)
async def sandbox() -> Dict:
    start = time.monotonic()
    q = Trade.read_all_sql()
    print(f'Query build took {time.monotonic() - start:.5f} seconds.')

    start = time.monotonic()
    df = pl.read_database_uri(q, DATABASE_URL)
    print(f'DB to DF took {time.monotonic() - start:.5f} seconds.')
    print(type(df))
    print(df.shape)
    print(df.head(5))

    return {
        'message': 'Sandbox tasks enqueued.',
    }
