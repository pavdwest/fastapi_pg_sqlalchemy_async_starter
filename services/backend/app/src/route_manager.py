from fastapi import FastAPI

from src.modules.home.routes import router as home_router
from src.modules.book.routes import router as book_router


def register_routes(app: FastAPI):
    app.include_router(home_router)
    app.include_router(book_router)
