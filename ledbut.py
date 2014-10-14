from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import sys #exit
import signal #signal

import myComm

def shutdown_server():
    print("\rYou pressed Ctrl+C!")
    #net.disconnect()
    sys.exit(0)
    
def signal_handler(signal, frame):
    shutdown_server()
    
print("Flask running...")
signal.signal(signal.SIGINT, signal_handler)
app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def onNetMsg(msg):
    print(msg)
    but = True if msg=='Button ON' else False
    socketio.emit('butRState', {'but': but}, namespace='/test')

def onSerialMsg(msg):
    print(msg)
    but = True if msg=='BUT oN' else False
    socketio.emit('butAState', {'but': but}, namespace='/test')

net = myComm.myNet()
net.onMsg = onNetMsg
#net.connect('192.168.1.91', 12345)
net.connect('10.0.0.4', 12345)

ser = myComm.mySerial()
ser.onMsg = onSerialMsg
ser.connect('/dev/ttyACM0')


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('my event', namespace='/test')
def test_message(message):
    print(message['data'])

@socketio.on('connect', namespace='/test')
def test_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

@socketio.on('ledRCtrl', namespace='/test')
def ledRCtrl(message):
    print(message['led'])
    if message['led']:
        net.sendMsg('l1')
    else:
        net.sendMsg('l0')

@socketio.on('ledACtrl', namespace='/test')
def ledACtrl(message):
    print(message['led'])
    if message['led']:
        ser.sendMsg('l1')
    else:
        ser.sendMsg('l0')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)
