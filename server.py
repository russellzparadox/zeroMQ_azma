import subprocess
import asyncio
import zmq
import zmq.asyncio
import json
import logging

# logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("server.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)


async def run_command_async(command_name, parameters):
    """Run a command asynchronously in a thread."""
    def run_command():
        return subprocess.run(
            [command_name] + parameters, capture_output=True, text=True
        )

    return await asyncio.to_thread(run_command)


async def process_request(socket, client_id, message):
    """Process a single client request."""
    logging.info(f"Processing request from client {client_id}: {message}")
    try:
        command_type = message.get('command_type')
        if command_type == 'os':
            command_name = message.get('command_name', None)
            parameters = message.get('parameters', [])
            # Run the OS command asynchronously
            res = await run_command_async(command_name, parameters)
            response = {
                'return_code': res.returncode,
                'output': res.stdout,
                'error': res.stderr
            }
            logging.info(f"Command executed: {command_name} {parameters}, Response: {response}")
        else:
            # Evaluate the expression
            expression = message.get('expression', None)
            result = eval(expression)
            response = {
                'return_code': 0,
                'output': str(result),
                'error': ''
            }
            logging.info(f"Expression evaluated: {expression}, Result: {result}")
    except Exception as e:
        response = {
            'return_code': -1,
            'output': '',
            'error': str(e)
        }
        logging.error(f"Error processing request from client {client_id}: {e}")

    # Send the response back to the client
    await socket.send_multipart([client_id, b"", json.dumps(response).encode('utf-8')])
    logging.info(f"Response sent to client {client_id}: {response}")


async def handle_requests(socket):
    """Handle incoming client requests in parallel."""
    while True:
        try:
            # Receive a message from a client
            client_id, _, message = await socket.recv_multipart()
            message = json.loads(message.decode('utf-8'))
            logging.info(f"Received request from client {client_id}: {message}")

            # Create a new task for each client request
            asyncio.create_task(process_request(socket, client_id, message))
        except Exception as e:
            logging.error(f"Error receiving request: {e}")


async def main():
    logging.info("Server starting...")
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind("tcp://*:5555")

    logging.info("Server ready to handle requests.")
    await handle_requests(socket)


if __name__ == '__main__':
    asyncio.run(main())
