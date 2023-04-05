import socket
import sys

PROMPT = """
Choose one of the followingg beetle actions:
  1. Gun
  2. Vest
  3. Glove
  4. Quit
Your choice: 
"""


# Communicates with eval_server
class Client:
    def __init__(self, server_name, server_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_name = server_name
        self.server_port = server_port

    def connect(self):
        self.socket.connect(("localhost", 8080))
        print("Connected to Ultra96 on local")

    def recv_game_state(self):
        game_state_received = None
        try:
            # recv length followed by '_' followed by cypher
            data = b""
            while not data.endswith(b"_"):
                _d = self.socket.recv(1)
                if not _d:
                    data = b""
                    break
                data += _d
            if len(data) == 0:
                print("no more data from the client")
                return None

            data = data.decode("utf8")
            length = int(data[:-1])

            data = b""
            while len(data) < length:
                _d = self.socket.recv(length - len(data))
                if not _d:
                    data = b""
                    break
                data += _d
            if len(data) == 0:
                print("no more data from the client")
                return None

            msg = data.decode("utf8")
            game_state_received = msg

        except ConnectionResetError:
            print("Connection Reset")
            return None

        return game_state_received

    def send_plaintext(self, plaintext):
        success = True

        m = str(len(plaintext)) + "_"
        try:
            self.socket.sendall(m.encode("utf8"))
            self.socket.sendall(plaintext.encode("utf8"))
        except OSError:
            print("Connection terminated")
            success = False
        return success

    def run(self):
        sensors = ["gun", "vest", "glove"]
        actions = {"gun": "shoot", "vest": "hit", "glove": "glove_movement"}

        sensor = ""
        player = ""

        while not player:
            user_input = input("Enter player (p1/p2): ")

            if user_input not in ["p1", "p2"]:
                print("Input invalid, try again")
                continue
            player = user_input

        while not sensor:
            user_input = input(PROMPT)

            if user_input not in "1234":
                print("Input invalid, try again")
                continue

            sensor = sensors[int(user_input) - 1]

        send_json = '{"player": "' + player + '", "sensor": "' + sensor + '"}'
        print("Sending", send_json)

        self.send_plaintext(send_json)

        receivedMsg = self.recv_game_state()
        if not receivedMsg:
            return

        print("From server:", receivedMsg)

        while True:
            user_input = input("Enter to continue/ q to quit: ")
            if user_input == "q":
                break

            send_json = "shoot"
            if sensor not in actions:
                break
            action = actions[sensor]

            if sensor == "glove":
                if user_input not in "012":
                    print("Wrong user input")
                    continue
                action = user_input

            print("Sending", action)
            self.send_plaintext(action)

            receivedMsg = self.recv_game_state()
            if not receivedMsg:
                break

            print("From server:", receivedMsg)

        self.socket.close()


if __name__ == "__main__":
    sensor = "gun"
    if len(sys.argv) == 2:
        sensor = sys.argv[1]
    client = Client("192.168.95.234", 8080)
    client.connect()
    client.run()
