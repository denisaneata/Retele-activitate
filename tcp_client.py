import socket

HOST = "127.0.0.1"
PORT = 3333
BUFFER = 1024


def read_response(sock):

    data = sock.recv(BUFFER)

    if not data:
        return None

    text = data.decode()

    try:
        size, message = text.split(" ", 1)
        expected = int(size)

        while len(message) < expected:
            more = sock.recv(BUFFER).decode()
            message += more

        return message

    except:
        return "Invalid server response"


def run_client():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print("Connected to server")
    print("Commands: ADD, GET, REMOVE, LIST, COUNT, CLEAR, UPDATE, POP, QUIT")

    while True:

        cmd = input(">> ")

        client.sendall(cmd.encode())

        reply = read_response(client)

        if reply is None:
            print("Server closed connection")
            break

        print("SERVER:", reply)

        if cmd.upper() == "QUIT":
            break

    client.close()


if __name__ == "__main__":
    run_client()