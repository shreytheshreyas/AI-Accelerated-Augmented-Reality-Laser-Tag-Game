import json
import multiprocessing as mp
import socket

from Helper import Actions
from HWAccel import HWAccel

from HWAccel_Stub import HWAccel_Stub
from Test import get_queue

COMPONENT_IDS = {
    "p1_gun": 0,
    "p1_vest": 1,
    "p1_glove": 2,
    "p2_gun": 3,
    "p2_vest": 4,
    "p2_glove": 5,
}


class RelayServer:
    def __init__(self, host, port, action_queue, update_beetle_queue):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.edit_conn_queue = mp.Queue()

        self.connected = mp.Array("i", [False] * 6)
        self.action_queue = action_queue
        self.update_beetle_queue = update_beetle_queue

        # TODO: Replace with actual HWAccel
        self.ai = HWAccel_Stub()
        # self.ai = HWAccel()

    def recv_msg(self, conn):
        msg = None
        try:
            # recv length followed by '_' followed by cypher
            data = b""
            while not data.endswith(b"_"):
                _d = conn.recv(1)
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
                _d = conn.recv(length - len(data))
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

    def send_plaintext(self, plaintext, conn):
        success = True

        m = str(len(plaintext)) + "_"
        try:
            conn.sendall(m.encode("utf-8"))
            conn.sendall(plaintext.encode("utf-8"))
        except OSError:
            print("Connection terminated")
            success = False
        return success

    def update(self, update_beetle_queue):
        while True:
            conn, data = update_beetle_queue.get()
            self.send_plaintext(data, conn)

    def handle_gun_conn(self, conn, action_queue, player, component):
        while True:
            msg = self.recv_msg(conn)
            if not msg:
                break
            # if msg != "shoot":
            #     print("wrong action (gun)")
            #     break

            action_queue.put((player, "shoot"))

        conn.close()
        with self.connected.get_lock():
            self.connected[COMPONENT_IDS[component]] = False
            print(f"Connection to {component} ended")

    def handle_vest_conn(self, conn, action_queue, player, component):
        while True:
            msg = self.recv_msg(conn)
            if not msg:
                break
            # if msg != "hit":
            #     print("Wrong action (hit)")
            #     break

            action_queue.put((player, "hit"))
            # self.send_plaintext(msg, conn)

        conn.close()
        with self.connected.get_lock():
            self.connected[COMPONENT_IDS[component]] = False
            print(f"Connection to {component} ended")

    def handle_glove_conn(self, conn, action_queue, player, component):
        while True:
            msg = self.recv_msg(conn)
            if not msg:
                break
            action = self.ai.get_action(msg)
            if action != Actions.no:
                action_queue.put((player, action))

        conn.close()
        with self.connected.get_lock():
            self.connected[COMPONENT_IDS[component]] = False
            print(f"Connection to {component} ended")

    def get_player_sensor(self, conn, addr):
        print(f"Accepted connection from {addr}")
        msg = self.recv_msg(conn)
        if not msg:
            return "", ""

        data = json.loads(msg)

        if "player" not in data or "sensor" not in data:
            print("Wrong connection type")
            conn.close()
            return "", ""

        sensor = data["sensor"]
        player = data["player"]
        component = player + "_" + sensor

        with self.connected.get_lock():
            id = COMPONENT_IDS[component]
            if self.connected[id]:
                print(f"{component} already connected")
                conn.close()
                return "", ""

            self.connected[id] = True
            self.send_plaintext(f"Server connection for {component} accepted", conn)

        return player, sensor

    def run(self):
        update_process = mp.Process(
            target=self.update,
            args=(
                self.update_beetle_queue,
                self.edit_conn_queue,
            ),
        )
        update_process.start()

        self.socket.bind((self.host, self.port))
        self.socket.listen(6)
        print(f"Listening on {self.host}:{self.port}...")

        while True:
            conn, addr = self.socket.accept()

            player, sensor = self.get_player_sensor(conn, addr)
            if player == "":
                conn.close()
                continue
            component = player + "_" + sensor
            print(f"Connected to {component}")
            self.edit_conn_queue.put((component, conn))

            if sensor == "gun":
                p = mp.Process(
                    target=self.handle_gun_conn,
                    args=(
                        conn,
                        self.action_queue,
                        self.edit_conn_queue,
                        player,
                        component,
                    ),
                )
                p.start()
            elif sensor == "vest":
                p = mp.Process(
                    target=self.handle_vest_conn,
                    args=(
                        conn,
                        self.action_queue,
                        self.edit_conn_queue,
                        player,
                        component,
                    ),
                )
                p.start()
            elif sensor == "glove":
                p = mp.Process(
                    target=self.handle_glove_conn,
                    args=(conn, self.action_queue, player, component),
                )
                p.start()


if __name__ == "__main__":
    action_queue = mp.Queue()
    update_beetle_queue = mp.Queue()

    relay_server = RelayServer("127.0.0.1", 8080, action_queue, update_beetle_queue)
    relay_server_process = mp.Process(target=relay_server.run)

    action_process = mp.Process(target=get_queue, args=(action_queue,))

    try:
        relay_server_process.start()
        relay_server_process.join()
    except KeyboardInterrupt:
        print("\nServer Stopped")
        relay_server_process.terminate()
