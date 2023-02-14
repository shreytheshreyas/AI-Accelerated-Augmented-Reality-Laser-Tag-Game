import socket
import sys

from sshtunnel import open_tunnel


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
        soc_tunnel = open_tunnel(
            ("stu.comp.nus.edu", 22),
            ssh_username="kaijiel",
            remote_bind_address=(self.server_name, 22),
            block_on_close=False,
        )
        soc_tunnel.start()
        print("Connected to SOC tunnel")

        ultra96_tunnel = open_tunnel(
            ssh_address_or_host=("127.0.0.1", soc_tunnel.local_bind_port),
            remote_bind_address=("127.0.0.1", self.server_port),
            # ssh_password="xilinxB13capstone",
            ssh_password="xilinx",
            ssh_username="xilinx",
            block_on_close=False,
        )
        ultra96_tunnel.start()
        print(ultra96_tunnel.local_bind_port)
        print("Connected to Ultra96 tunnel")

        self.socket.connect(("localhost", ultra96_tunnel.local_bind_port))
        print("Connected to server on Ultra96")

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

        while not sensor:
            user_input = input(PROMPT.strip())

            if user_input not in "1234":
                print("Input invalid, try again")
                continue

            sensor = sensors[int(user_input) - 1]
            send_json = '{"player": "p1", "sensor": "' + sensor + '"}'

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

            print("Sending", action)
            self.send_plaintext(action)

            receivedMsg = self.recv_game_state()
            if not receivedMsg:
                break

            print("From server:", receivedMsg)

        self.socket.close()


if __name__ == "__main__":
    client = Client("192.168.95.250", 8080)
    client.connect()
    client.run()
