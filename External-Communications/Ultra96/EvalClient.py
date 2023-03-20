import base64
import json
import multiprocessing as mp
import socket
import time

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from Test import get_queue, put_queue


class EvalClient:
    def __init__(self, server_name, server_port, req_queue, resp_queue):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secret_key = "PLSPLSPLSPLSWORK"
        self.iv = Random.new().read(AES.block_size)
        self.req_queue = req_queue
        self.resp_queue = resp_queue

        self.server_name = server_name
        self.server_port = server_port

        self.connected = False

    def connect(self):
        while not self.connected:
            try:
                self.socket.connect((self.server_name, self.server_port))
                self.connected = True
            except ConnectionRefusedError:
                print("Connection refused. Retrying in 1 second...", end="\r")
                time.sleep(1)

        print(f"Connected to Eval Server at {self.server_name}:{self.server_port}")

    def send_ciphertext(self, plaintext):
        success = True

        cipher = AES.new(self.secret_key.encode("utf-8"), AES.MODE_CBC, self.iv)
        padded_pt = pad(plaintext.encode("utf-8"), AES.block_size)
        ciphertext = base64.b64encode(self.iv + cipher.encrypt(padded_pt))

        m = str(len(ciphertext)) + "_"
        try:
            self.socket.sendall(m.encode("utf-8"))
            self.socket.sendall(ciphertext)
        except OSError:
            print("Connection terminated")
            success = False
        return success

    def recv_msg(self):
        msg = None
        try:
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

            msg = data.decode("utf-8")

        except ConnectionResetError:
            print("Connection Reset")
            return None

        return msg

    def run(self):
        while True:
            eval_data = self.req_queue.get()
            eval_json = json.dumps(eval_data)
            self.send_ciphertext(eval_json)

            recv_json = self.recv_msg()
            if not recv_json:
                break

            recv_data = json.loads(recv_json)
            self.resp_queue.put(recv_data)

        self.socket.close()


if __name__ == "__main__":
    eval_data = [
        {
            "p1": {
                "hp": 100,
                "action": "none",
                "bullets": 6,
                "grenades": 2,
                "shield_time": 0,
                "shield_health": 0,
                "num_deaths": 0,
                "num_shield": 3,
            },
            "p2": {
                "hp": 100,
                "action": "none",
                "bullets": 6,
                "grenades": 2,
                "shield_time": 0,
                "shield_health": 0,
                "num_deaths": 0,
                "num_shield": 3,
            },
        }
    ] * 4

    req_queue = mp.Queue()
    resp_queue = mp.Queue()

    client = EvalClient("127.0.0.1", 2108, req_queue, resp_queue)
    client.connect()

    eval_process = mp.Process(target=client.run)
    req_process = mp.Process(
        target=put_queue,
        args=(
            req_queue,
            eval_data,
        ),
    )
    resp_process = mp.Process(target=get_queue, args=(resp_queue,))

    try:
        eval_process.start()
        req_process.start()
        resp_process.start()

        eval_process.join()
        req_process.join()
        resp_process.join()
    except KeyboardInterrupt:
        print("\nClient Stopped")
        eval_process.terminate()
        req_process.terminate()
        resp_process.terminate()
