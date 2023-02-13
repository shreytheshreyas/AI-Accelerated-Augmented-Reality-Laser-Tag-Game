import base64
import json
import socket

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class EvalClient:
    def __init__(self, req_queue, resp_queue):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secret_key = "PLSPLSPLSPLSWORK"
        self.iv = Random.new().read(AES.block_size)
        self.req_queue = req_queue
        self.resp_queue = resp_queue

    def connect(self, serverName, serverPort):
        self.socket.connect((serverName, serverPort))

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

            msg = data.decode("utf-8")  # Decode raw bytes to UTF-8
            game_state_received = msg

        except ConnectionResetError:
            print("Connection Reset")
            return None

        return game_state_received

    def send_ciphertext(self, plaintext):
        success = True

        cipher = AES.new(self.secret_key.encode("utf-8"), AES.MODE_CBC, self.iv)
        padded_pt = pad(plaintext.encode("utf-8"), AES.block_size)
        ciphertext = base64.b64encode(self.iv + cipher.encrypt(padded_pt))

        # ice_print_debug(f"Sending message to client: {plaintext} (Unencrypted)")
        # send len followed by '_' followed by cypher
        m = str(len(ciphertext)) + "_"
        try:
            self.socket.sendall(m.encode("utf-8"))
            self.socket.sendall(ciphertext)
        except OSError:
            print("Connection terminated")
            success = False
        return success

    def run(self):
        while True:
            # user_input = input("enter to continue/ q to quit: ")
            # if user_input == "q":
            #     break
            eval_data = self.req_queue.get()
            eval_json = json.dumps(eval_data)
            self.send_ciphertext(eval_json)

            recv_json = self.recv_game_state()
            if not recv_json:
                break

            print("From server:", recv_json)
            recv_data = json.loads(recv_json)
            self.resp_queue.put(recv_data)

        self.socket.close()


if __name__ == "__main__":
    client = EvalClient()
    client.connect("127.0.0.1", 2105)
    client.run()
