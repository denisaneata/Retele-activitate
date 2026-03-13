import socket

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


def receive_full_message(sock):
    try:
        data = sock.recv(BUFFER_SIZE)

        if not data:
            return None

        string_data = data.decode('utf-8')

        first_space = string_data.find(' ')

        if first_space == -1 or not string_data[:first_space].isdigit():
            return "Invalid response format"

        message_length = int(string_data[:first_space])
        message = string_data[first_space + 1:]

        remaining = message_length - len(message)

        while remaining > 0:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                break
            message += data.decode('utf-8')
            remaining -= len(data)

        return message

    except Exception as e:
        return f"Error: {e}"


def main():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

        client_socket.connect((HOST, PORT))

        print("Connected to server")
        print("Commands available:")
        print("ADD key value")
        print("GET key")
        print("REMOVE key")
        print("LIST")
        print("COUNT")
        print("CLEAR")
        print("UPDATE key value")
        print("POP key")
        print("QUIT")

        while True:

            command = input("client> ").strip()

            if not command:
                continue

            client_socket.sendall(command.encode('utf-8'))

            if command.lower() == "quit":
                print("Connection closed.")
                break

            response = receive_full_message(client_socket)

            if response is None:
                print("Server closed connection.")
                break

            print("Server response:", response)


if __name__ == "__main__":
    main()
