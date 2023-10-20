from src.app import App
from src.route_manager import register_routes
from src.models import AppModel


# Custom Startup & Shutdown Handlers
async def startup():
    await AppModel.init_orm()

    # Register routes with app
    register_routes(app=app)


async def shutdown():
    # await db.shutdown()
    pass


# Create app instance
app = App(
    on_startup_handlers=[startup],
    on_shutdown_handlers=[shutdown]
).get()
