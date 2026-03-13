import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return "OK record added"

    def get(self, key):
        with self.lock:
            if key in self.data:
                return f"DATA {self.data[key]}"
            return "ERROR invalid key"

    def remove(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return "OK value deleted"
            return "ERROR invalid key"

    def list(self):
        with self.lock:
            if not self.data:
                return "DATA|"
            result = ",".join(f"{k}={v}" for k, v in self.data.items())
            return f"DATA|{result}"

    def count(self):
        with self.lock:
            return f"DATA {len(self.data)}"

    def clear(self):
        with self.lock:
            self.data.clear()
        return "all data deleted"

    def update(self, key, value):
        with self.lock:
            if key in self.data:
                self.data[key] = value
                return "Data updated"
            return "ERROR invalid key"

    def pop(self, key):
        with self.lock:
            if key in self.data:
                value = self.data.pop(key)
                return f"DATA {value}"
            return "ERROR invalid key"


state = State()


def process_command(command):
    parts = command.split()

    if not parts:
        return "ERROR empty command"

    cmd = parts[0].lower()

    try:

        if cmd == "add":
            if len(parts) < 3:
                return "ERROR invalid command format"
            key = parts[1]
            value = " ".join(parts[2:])
            return state.add(key, value)

        elif cmd == "get":
            if len(parts) != 2:
                return "ERROR invalid command format"
            return state.get(parts[1])

        elif cmd == "remove":
            if len(parts) != 2:
                return "ERROR invalid command format"
            return state.remove(parts[1])

        elif cmd == "list":
            return state.list()

        elif cmd == "count":
            return state.count()

        elif cmd == "clear":
            return state.clear()

        elif cmd == "update":
            if len(parts) < 3:
                return "ERROR invalid command format"
            key = parts[1]
            value = " ".join(parts[2:])
            return state.update(key, value)

        elif cmd == "pop":
            if len(parts) != 2:
                return "ERROR invalid command format"
            return state.pop(parts[1])

        elif cmd == "quit":
            return "Server closing connection"

        else:
            return "ERROR unknown command"

    except Exception as e:
        return f"ERROR {str(e)}"


def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode('utf-8').strip()

                if command.lower() == "quit":
                    response = "Server closing connection"
                    response_data = f"{len(response)} {response}".encode('utf-8')
                    client_socket.sendall(response_data)
                    break

                response = process_command(command)

                response_data = f"{len(response)} {response}".encode('utf-8')
                client_socket.sendall(response_data)

            except Exception as e:
                error = f"ERROR {str(e)}"
                client_socket.sendall(f"{len(error)} {error}".encode('utf-8'))
                break


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[SERVER] Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
