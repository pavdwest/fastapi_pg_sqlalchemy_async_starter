from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.logging.service import logger
from src.config import PROJECT_NAME
from src.helpers.route_manager import register_routes
from src.database.service import DatabaseService
from src.modules.arqueue.bus import Bus


# App lifespan context manager
@asynccontextmanager
async def lifespan_ctx(app: FastAPI):
    logger.info("Starting up...")
    app.state.db = DatabaseService.get()
    await Bus.init()
    register_routes(app=app)
    yield
    logger.info("Shutting down...")


# Create app instance
app = FastAPI(
    title=PROJECT_NAME,
    lifespan=lifespan_ctx
)
