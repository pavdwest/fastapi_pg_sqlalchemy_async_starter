from fastapi import FastAPI

from src.modules.home.routes import router as home_router
from src.admin.routes import router as admin_router
from src.tenant.routes import router as tenant_router
from src.login.routes import router as login_router
from src.login.routes import wtf_router as login_router_wtf
from src.modules.book.routes import router as book_router
from src.modules.critic.routes import router as critic_router
from src.modules.review.routes import router as review_router
from src.modules.arqueue.routes import router as arqueue_router


def register_routes(app: FastAPI):
    app.include_router(home_router)
    app.include_router(admin_router)
    app.include_router(tenant_router)
    app.include_router(login_router_wtf)
    app.include_router(login_router)
    app.include_router(book_router)
    app.include_router(critic_router)
    app.include_router(review_router)
    app.include_router(arqueue_router)
