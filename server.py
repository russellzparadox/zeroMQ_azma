#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
import subprocess
import asyncio
import time
import zmq
import zmq.asyncio
import json
import os


async def handle_request(socket):
    while True:
        message = await socket.recv_json()
        message = json.loads(message)
        print(message)
        command_type = message.get('command_type')
        if command_type == 'os':
            command_name = message.get('command_name', None)
            parameters = message.get('parameters', [])
            res = subprocess.run([command_name, ] + parameters, capture_output=True, text=True)
            response = {
                'return_code': res.returncode,
                'output': res.stdout,
                'error': res.stderr
            }
            print(response)
            await socket.send_json(json.dumps(response))
        else:
            expression = message.get('expression', None)
            print(eval(expression))
            await socket.send(eval(expression))


async def main():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    await handle_request(socket)


if __name__ == '__main__':
    asyncio.run(main())

#
#
# while True:
#     #  Wait for next request from client
#     message = json.loads(socket.recv_json())
#     print(f"Received request: {message}")
#     if message['command_type'] == 'os':
#         message['parameters'].insert(0, message['command_name'])
#         print(message['parameters'])
#         # print(message['command_name']+' '+' '.join(message['parameters']))
#         subprocess.run(message['parameters'])
#         # os.system(message['command']+' '.join(message['parameter']))
#     if message['command_type'] == 'compute':
#         response = eval(message['expression'])
#         socket.send_json(response)
#
#     #  Do some 'work'
#     time.sleep(1)
#
#     #  Send reply back to client
#     socket.send(b"World")
