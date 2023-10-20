from __future__ import annotations
from typing import Callable, List
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI

from src.config import PROJECT_NAME
from src.logging.service import logger


class App:
    @lru_cache(maxsize=1)
    def get(self) -> App:
        return self._instance

    def __init__(
        self,
        on_startup_handlers: List[Callable] = None,
        on_shutdown_handlers: List[Callable] = None,
    ) -> None:
        self.on_startup_handlers = on_startup_handlers
        self.on_shutdown_handlers = on_shutdown_handlers

        @asynccontextmanager
        async def lifespan_ctx(app: FastAPI):
            logger.info("Starting up...")
            for i in self.on_startup_handlers:
                await i()
            yield
            logger.info("Shutting down...")
            for i in self.on_shutdown_handlers:
                await i()

        self._instance = FastAPI(
            title=PROJECT_NAME,
            lifespan=lifespan_ctx
        )
