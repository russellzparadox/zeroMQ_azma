import zmq
import json
import logging
import shlex

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


def send_request(socket, message):
    """
    Send a request to the server and wait for a response.

    :param socket: ZMQ socket.
    :param message: Message to send as a dictionary.
    :return: Response from the server.
    """
    socket.send_json(message)
    reply = socket.recv()
    return json.loads(reply.decode('utf-8'))


def main():
    context = zmq.Context()

    # Create a REQ socket
    logging.info("Connecting to the server...")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    print("Welcome to the CLI client. Type 'exit' to quit.")
    print("Commands can be:")
    print("  1. OS commands: Type 'os <command> <parameters>' (e.g., os ping google.com -c 2).")
    print("  2. Python expressions: Type 'expr <expression>' (e.g., expr 2 + 2).")

    while True:
        user_input = input(">> ").strip()
        if user_input.lower() == "exit":
            print("Exiting the client. Goodbye!")
            break

        try:
            # Parse input
            if user_input.startswith("os "):
                parts = shlex.split(user_input)  # Split command safely
                command_name = parts[1]
                parameters = parts[2:]
                message = {
                    "command_type": "os",
                    "command_name": command_name,
                    "parameters": parameters
                }
            elif user_input.startswith("expr "):
                expression = user_input[len("expr "):].strip()
                message = {
                    "command_type": "expr",
                    "expression": expression
                }
            else:
                print("Invalid input. Use 'os <command>' or 'expr <expression>'.")
                continue

            # Send request to server
            response = send_request(socket, message)
            if response['return_code'] == 0:
                print(f"{response['output']}")
            else:
                print(f"{response['error']}")
        except Exception as e:
            logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()
