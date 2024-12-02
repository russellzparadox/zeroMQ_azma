#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
import subprocess
import time
import zmq
import json
import os
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = json.loads(socket.recv_json())
    print(f"Received request: {message}")
    if message['command_type'] == 'os':
        message['parameters'].insert(0, message['command_name'])
        print(message['parameters'])
        # print(message['command_name']+' '+' '.join(message['parameters']))
        subprocess.run(message['parameters'])
        # os.system(message['command']+' '.join(message['parameter']))
    if message['command_type'] == 'compute':
        response = eval(message['expression'])
        socket.send_json(response)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send(b"World")
