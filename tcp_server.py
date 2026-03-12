import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER = 1024


class ProductStore:
    def __init__(self):
        self.products = {}
        self.mutex = threading.Lock()

    def add_product(self, key, value):
        with self.mutex:
            if key in self.products:
                return "ERROR key already exists"
            self.products[key] = value
            return "OK record added"

    def get_product(self, key):
        with self.mutex:
            if key not in self.products:
                return "ERROR invalid key"
            return f"DATA {self.products[key]}"

    def delete_product(self, key):
        with self.mutex:
            if key not in self.products:
                return "ERROR invalid key"
            del self.products[key]
            return "OK value deleted"

    def list_products(self):
        with self.mutex:
            if not self.products:
                return "DATA empty"
            pairs = [f"{k}={v}" for k, v in self.products.items()]
            return "DATA|" + ",".join(pairs)

    def count_products(self):
        with self.mutex:
            return f"DATA {len(self.products)}"

    def clear_all(self):
        with self.mutex:
            self.products.clear()
            return "OK all data deleted"

    def update_product(self, key, value):
        with self.mutex:
            if key not in self.products:
                return "ERROR invalid key"
            self.products[key] = value
            return "OK data updated"

    def pop_product(self, key):
        with self.mutex:
            if key not in self.products:
                return "ERROR invalid key"
            value = self.products.pop(key)
            return f"DATA {value}"


store = ProductStore()


def execute_command(text):
    parts = text.split()

    if not parts:
        return "ERROR empty command"

    command = parts[0].upper()

    try:

        if command == "ADD":
            key = parts[1]
            value = " ".join(parts[2:])
            return store.add_product(key, value)

        elif command == "GET":
            return store.get_product(parts[1])

        elif command == "REMOVE":
            return store.delete_product(parts[1])

        elif command == "LIST":
            return store.list_products()

        elif command == "COUNT":
            return store.count_products()

        elif command == "CLEAR":
            return store.clear_all()

        elif command == "UPDATE":
            key = parts[1]
            value = " ".join(parts[2:])
            return store.update_product(key, value)

        elif command == "POP":
            return store.pop_product(parts[1])

        elif command == "QUIT":
            return "QUIT"

        else:
            return "ERROR unknown command"

    except IndexError:
        return "ERROR invalid parameters"


def client_handler(sock):
    with sock:
        while True:
            data = sock.recv(BUFFER)

            if not data:
                break

            request = data.decode().strip()
            response = execute_command(request)

            if response == "QUIT":
                message = "Connection closed"
                payload = f"{len(message)} {message}".encode()
                sock.sendall(payload)
                break

            payload = f"{len(response)} {response}".encode()
            sock.sendall(payload)


def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server running on {HOST}, port:{PORT}")

    while True:
        client, addr = server.accept()
        print("Client connected:", addr)

        thread = threading.Thread(target=client_handler, args=(client,))
        thread.start()


if __name__ == "__main__":
    start()