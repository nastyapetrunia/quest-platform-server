from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/health")
def health():
    return "healthy", 200

@socketio.on("message")
def echo_message(msg):
    socketio.send(f"Echo: {msg}")
