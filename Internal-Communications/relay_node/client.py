import socket

from sshtunnel import open_tunnel


PROMPT = """Choose one of the followingg beetle actions:
  1. Gun
  2. Vest
  3. Glove
  4. Quit
Your choice: """


# Communicates with eval_server
class LaptopClient:
    def __init__(self, server_name, server_port):
        self.server_name = server_name
        self.server_port = server_port
        self.socket = None
        self.ssh_tunnel = None
        self.server_tunnel = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.5)

        self.ssh_tunnel = open_tunnel(
            ("stu.comp.nus.edu", 22),
            ssh_username="kaijiel",
            remote_bind_address=(self.server_name, 22),
        )
        self.ssh_tunnel.start()
        print("Set up tunnel to Ultra96")

        self.server_tunnel = open_tunnel(
            ssh_address_or_host=("127.0.0.1", self.ssh_tunnel.local_bind_port),
            remote_bind_address=("127.0.0.1", self.server_port),
            # ssh_password="xilinxB13capstone",
            ssh_password="xilinx",
            ssh_username="xilinx",
        )
        self.server_tunnel.start()
        print("Set up tunnel to Server on Ultra96")

        # print("local bind port =", self.server_tunnel.local_bind_port)
        self.socket.connect(("localhost", self.server_tunnel.local_bind_port))
        print("Connected to server on Ultra96")

    def close(self):
        self.server_tunnel.close()
        self.ssh_tunnel.close()
        self.ssh_tunnel = None
        self.server_tunnel = None
        self.socket.close()
        self.socket = None

    def available(self):
        try:
            _d = self.socket.recv(1)
            return True, _d
        except socket.timeout:
            return False, ""

    def recv_msg(self, d):
        msg = None
        try:
            # recv length followed by '_' followed by cypher
            data = d
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

        except ConnectionResetError:
            print("Connection Reset")
            return None

        return msg

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

    def send_empty(self):
        try:
            self.socket.sendall("".encode("utf8"))
        except OSError:
            print("Connection terminated")

    def run_test(self):
        sensors = ["gun", "vest", "glove"]
        actions = {"gun": "shoot", "vest": "hit", "glove": "glove_movement"}

        sensor = ""

        while not sensor:
            user_input = input()
            if user_input not in "1234":
                print("Input invalid, try again")
                continue

            # put this in the connection established
            sensor = sensors[int(user_input) - 1]
            send_json = '{"player": "p1", "sensor": "' + sensor + '"}'

            print("Sending", send_json)
            self.send_plaintext(send_json)

        receivedMsg = self.recv_msg("")
        if not receivedMsg:
            return

        print("From server:", receivedMsg)
        self.running = True

        while self.running:
            user_input = input("Enter to continue/ q to quit: ")
            if user_input == "q":
                break
            send_json = "shoot"
            if sensor not in actions:
                break
            action = actions[sensor]

            print("Sending", action)
            self.send_plaintext(action)

            avail, first = self.laptopClient.available()
            if avail:
                self.laptopClient.recv_msg(first)
            if not receivedMsg:
                break

            print("From server:", receivedMsg)

        self.socket.close()

    def stop(self):
        self.running = False


if __name__ == "__main__":
    client = LaptopClient("192.168.95.250", 8080)
    client.connect()

    try:
        client.run_test()
    except KeyboardInterrupt:
        client.stop()
