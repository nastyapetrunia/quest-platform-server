from flask import Flask
from flask_socketio import SocketIO
from flask_restx import Api
from src.routes.auth_routes import auth_ns
from src.routes.general_routes import general_ns

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

api = Api(app, version='1.0', title='MVP Quests API',
          description='API for MVP Quests services.',
          doc='/swagger/')

api.add_namespace(auth_ns)
api.add_namespace(general_ns)

@socketio.on("message")
def echo_message(msg):
    socketio.send(f"Echo: {msg}")
