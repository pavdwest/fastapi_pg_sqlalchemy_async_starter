from src.app import app

from src.database.service import db
from src.route_manager import register_app
from src.models import AppModel


@app.on_event('startup')
async def startup():
    await AppModel.init_orm()


@app.on_event('shutdown')
async def startup():
    await db.shutdown()


# Register routes with app
register_app(app=app)
