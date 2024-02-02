from __future__ import annotations

from fastapi import FastAPI

from src.config import PROJECT_NAME
from src.logging.service import logger


def create_app() -> FastAPI:
    return FastAPI(
        title=PROJECT_NAME,
    )
