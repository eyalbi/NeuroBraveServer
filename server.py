from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import logging
import os
#creating a flask app and configure logging
app = Flask(__name__)
logging.basicConfig(filename='server.log', level=logging.DEBUG)
# initialize socket
socketio = SocketIO(app, cors_allowed_origins="*")

#default Flask home page rendering the html to the client and passing room token to JS
@app.route('/')
def index():
    token = request.args.get('token')
    port = int(os.environ.get("PORT", 17995))
    return render_template("index.html", token=token,port=port)

#logging connection to socket
@socketio.on('connect')
def on_connect():
    app.logger.info(f"User with requessid {request.sid} connected to socket")

#handle clients room registration
@socketio.on('join_room')
def handle_join_room(data):
    try:
        room = data['room']
        join_room(room)
        app.logger.debug(f"Client {request.sid} joined room {room}")
    except KeyError as e:
        app.logger.info(f"Missing Room Token {e}")
    except Exception as e:
        app.logger.exception(e)

#Handle send data stream and emiting
@socketio.on('send_data')
def handle_data(data):
    try:
        room = data['token']
        if data['type'] == 'mouse':
             # Here we emit mouse data to rooms for JS client visualization
            emit('update_mouse', data['data'], room=room)
        elif data['type'] == 'cpu':
            # Here we emit CPU data to rooms for JS client visualization
            emit('update_cpu', data['data'], room=room)
    except Exception as e:
        app.logger.exception(e)

if __name__ == '__main__':
    #for local run
    socketio.run(app, host='0.0.0.0', port=8765, keyfile='server.key', certfile='server.cert')
