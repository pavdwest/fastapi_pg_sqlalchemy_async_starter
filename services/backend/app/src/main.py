from src.app import create_app
from src.helpers.route_manager import register_routes
from src.modules.arqueue.bus import Bus
from src.database.service import DatabaseService

app = create_app()
register_routes(app)
db = DatabaseService()
