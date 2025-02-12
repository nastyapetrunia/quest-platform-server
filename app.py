from flask import Flask
from flask_socketio import SocketIO
from flask_restx import Api
from flask_cors import CORS

from src.database.utils.setup import logger
from src.routes.auth_routes import auth_ns
from src.routes.user_routes import user_ns
from src.routes.general_routes import general_ns
from src.routes.quest_routes import quest_ns, quests_ns

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers="*")

api = Api(app, version='1.0', title='MVP Quests API',
          description='API for MVP Quests services.',
          doc='/swagger/',
          authorizations={"JWT": {"type": "apiKey", "in": "header", "name": "Authorization", "description": "Type: Bearer your_token"}})

api.add_namespace(auth_ns)
api.add_namespace(user_ns)
api.add_namespace(quest_ns)
api.add_namespace(quests_ns)
api.add_namespace(general_ns)

@socketio.on("progressUpdate")
def handle_message(data):
    """
    Handles incoming messages and emits a userProgressUpdate event.

    :param data: JSON object received from the client.
    """
    if isinstance(data, dict):
        socketio.emit("userProgressUpdate", {"status": "success", "received": data})
    else:
        socketio.emit("userProgressUpdate", {"status": "error", "received": data})
