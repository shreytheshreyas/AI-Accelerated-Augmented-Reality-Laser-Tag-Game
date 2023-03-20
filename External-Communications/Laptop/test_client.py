import socket
import sys

import sshtunnel


# Communicates with eval_server
class Client:
    def __init__(self, sensor, serverName, serverPort):
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sensor = sensor
        self.actions = {"gun": "shoot", "vest": "hit", "glove": "action"}
        self.serverName = serverName
        self.serverPort = serverPort

    def connect(self):
        soc_tunnel = sshtunnel.open_tunnel(
            ("sunfire.comp.nus.edu.sg", 22),
            ssh_username="kaijiel",
            ssh_private_key="/home/kj/.ssh/id_rsa",
            remote_bind_address=("192.168.95.236", 22),
            block_on_close=False,
        )
        soc_tunnel.start()
        print("Connected to SOC tunnel")

        ultra96_tunnel = sshtunnel.open_tunnel(
            # ssh into xilinx
            ssh_address_or_host=("127.0.0.1", soc_tunnel.local_bind_port),
            # binds xilinx host
            remote_bind_address=("127.0.0.1", soc_tunnel.PORT),
            ssh_username="xilinx",
            ssh_private_key="/home/kj/.ssh/id_rsa_soc",
            local_bind_address=("127.0.0.1", SSH_TUNNEL_PORT),
            block_on_close=False,
        )
        ultra96_tunnel.start()
        print(ultra96_tunnel.local_bind_port)
        print("Connected to Ultra96 tunnel")

        self.socket.connect((self.serverName, self.serverPort))

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

            data = data.decode("utf-8")
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

            msg = data.decode("utf8")  # Decode raw bytes to UTF-8
            game_state_received = msg

        except ConnectionResetError:
            print("Connection Reset")
            return None

        return game_state_received

    def send_plaintext(self, plaintext):
        success = True

        m = str(len(plaintext)) + "_"
        try:
            self.socket.sendall(m.encode("utf-8"))
            self.socket.sendall(plaintext.encode("utf-8"))
        except OSError:
            print("Connection terminated")
            success = False
        return success

    def run(self):
        send_json = '{"player": "p1", "sensor": "' + self.sensor + '"}'
        self.send_plaintext(send_json)

        receivedMsg = self.recv_game_state()
        if not receivedMsg:
            return

        print("From server:", receivedMsg)

        while True:
            user_input = input("Enter to continue/ q to quit: ")
            if user_input == "q":
                break
            # f = open("send.json")
            # send_json = f.read()
            # f.close()

            send_json = "shoot"
            if self.sensor not in self.actions:
                break
            action = self.actions[self.sensor]

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
    print(sensor)
    client = Client(sensor)
    client.connect("127.0.0.1", 8080)
    client.run()
