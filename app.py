from flask import Flask
from flask_socketio import SocketIO
from flask_restx import Api
from flask_cors import CORS

from src.routes.auth_routes import auth_ns
from src.routes.user_routes import user_ns
from src.routes.quest_routes import quest_ns
from src.routes.general_routes import general_ns

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers="*")

api = Api(app, version='1.0', title='MVP Quests API',
          description='API for MVP Quests services.',
          doc='/swagger/')

api.add_namespace(auth_ns)
api.add_namespace(user_ns)
api.add_namespace(general_ns)
api.add_namespace(quest_ns)

@socketio.on("message")
def echo_message(msg):
    socketio.send(f"Echo: {msg}")
