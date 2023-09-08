from src.app import app
from src.route_manager import register_routes
from src.models import AppModel


@app.on_event('startup')
async def startup():
    await AppModel.init_orm()

    # Register routes with app
    register_routes(app=app)


@app.on_event('shutdown')
async def startup():
    # await db.shutdown()
    pass
