import json
import multiprocessing as mp
import socket
import time

from Helper import Actions

from HWAccel import HWAccel
from Test import get_queue

COMPONENT_IDS = {
    "p1_gun": 0,
    "p1_vest": 1,
    "p1_glove": 2,
    "p2_gun": 3,
    "p2_vest": 4,
    "p2_glove": 5,
}

SENSOR_MAPPING = {"gun": "bullets", "vest": "hp"}


class RelayServer:
    def __init__(
        self,
        host,
        port,
        action_queue,
        update_beetle_queue,
        connected,
        action_console_queue,
        logs_queue,
    ):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.edit_conn_queue = mp.Queue()
        self.connected = connected
        self.action_queue = action_queue
        self.action_console_queue = action_console_queue
        self.update_beetle_queue = update_beetle_queue
        self.logs_queue = logs_queue

        self.glove_in_queue = {
            "p1": mp.Queue(),
            "p2": mp.Queue(),
        }
        self.glove_out_queue = {
            "p1": mp.Queue(),
            "p2": mp.Queue(),
        }

        self.ai = HWAccel(
            self.glove_in_queue["p1"],
            self.glove_in_queue["p2"],
            self.glove_out_queue["p1"],
            self.glove_out_queue["p2"],
            self.logs_queue,
        )

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
                self.logs_queue.put("no more data from the client")
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
                self.logs_queue.put("no more data from the client")
                return None

            msg = data.decode("utf8")

        except ConnectionResetError:
            self.logs_queue.put("Connection Reset")
            return None

        return msg

    def send_plaintext(self, plaintext, conn):
        success = True

        m = str(len(plaintext)) + "_"
        try:
            conn.sendall(m.encode("utf-8"))
            conn.sendall(plaintext.encode("utf-8"))
        except OSError:
            self.logs_queue.put("Connection terminated")
            success = False
        return success

    def update_beetles(self):
        conns = {
            "p1_gun": None,
            "p1_vest": None,
            "p2_gun": None,
            "p2_vest": None,
        }

        while True:
            if not self.edit_conn_queue.empty():
                component, conn = self.edit_conn_queue.get()
                conns[component] = conn

            if not self.update_beetle_queue.empty():
                component, data = self.update_beetle_queue.get()
                self.logs_queue.put(
                    f"Get from update beetle queue [{data}] {component}"
                )
                time.sleep(0.2)
                with self.connected.get_lock():
                    if self.connected[COMPONENT_IDS[component]]:
                        self.logs_queue.put(f"Sending data [{data}] to {component}")
                        self.send_plaintext(str(data), conns[component])
                    else:
                        self.logs_queue.put(
                            f"Could not send data [{data}] to {component}"
                        )

    def update_conn_status(self, msg, component):
        if msg == "start":
            with self.connected.get_lock():
                self.connected[COMPONENT_IDS[component]] = True
                player, sensor = component.split("_")
                if sensor == "gun" or sensor == "vest":
                    self.logs_queue.put("put connn in action queue")
                    self.action_queue.put((player, "conn_" + sensor))

                self.logs_queue.put(f"Connected to {component}")
            return True

        if msg == "end":
            with self.connected.get_lock():
                self.connected[COMPONENT_IDS[component]] = False
                self.logs_queue.put(f"Disconnected from {component}")
            return True

        return False

    def handle_gun_conn(self, conn, player, component):
        while True:
            msg = self.recv_msg(conn)
            if not msg:
                break
            if self.update_conn_status(msg, component):
                continue
            if msg != "shoot":
                self.logs_queue.put("wrong action (gun)")
                continue

            self.action_queue.put((player, "shoot"))
            self.action_console_queue.put((player, "shoot"))

        conn.close()
        with self.connected.get_lock():
            self.connected[COMPONENT_IDS[component]] = False
            self.logs_queue.put(f"Disconnected from {component}")

    def handle_vest_conn(self, conn, player, component):
        while True:
            msg = self.recv_msg(conn)
            if not msg:
                break
            if self.update_conn_status(msg, component):
                continue

            if msg != "hit":
                self.logs_queue.put("wrong action (vest)")
                continue

            self.action_queue.put((player, "hit"))
            self.action_console_queue.put((player, "hit"))

        conn.close()
        with self.connected.get_lock():
            self.connected[COMPONENT_IDS[component]] = False
            self.logs_queue.put(f"Disconnected from {component}")

    def handle_glove_conn(self, conn, in_queue, out_queue, player, component):
        while True:
            msg = self.recv_msg(conn)
            if not msg:
                break
            if self.update_conn_status(msg, component):
                continue

            data = json.loads(msg)

            in_queue.put(list(data.values())[1:])

            action = out_queue.get()

            if action != Actions.no:
                self.action_queue.put((player, action))
                self.action_console_queue.put((player, action))

        conn.close()
        with self.connected.get_lock():
            self.connected[COMPONENT_IDS[component]] = False
            self.logs_queue.put(f"Disconnected from {component}")

    def init_conn(self, conn, addr):
        self.logs_queue.put(f"Accepted connection from {addr}")
        msg = self.recv_msg(conn)
        if not msg:
            return "", ""

        player, sensor = msg.split("_")
        component = msg

        with self.connected.get_lock():
            id = COMPONENT_IDS[component]
            if self.connected[id]:
                self.logs_queue.put(f"{component} already connected")
                conn.close()
                return "", ""

            self.connected[id] = True
            self.send_plaintext(f"Server connection for {component} accepted", conn)

        if sensor == "gun" or sensor == "vest":
            self.edit_conn_queue.put((component, conn))

        return player, sensor

    def run(self):
        update_process = mp.Process(
            target=self.update_beetles,
        )
        update_process.start()

        self.socket.bind((self.host, self.port))
        self.socket.listen(6)
        self.logs_queue.put(f"Listening on {self.host}:{self.port}...")

        while True:
            conn, addr = self.socket.accept()

            player, sensor = self.init_conn(conn, addr)
            if player == "":
                conn.close()
                continue
            component = player + "_" + sensor
            self.logs_queue.put(f"Connection to {component} thread initilised")

            if sensor == "gun":
                p = mp.Process(
                    target=self.handle_gun_conn,
                    args=(
                        conn,
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
                        player,
                        component,
                    ),
                )
                p.start()

            elif sensor == "glove":
                player_ai = getattr(self.ai, player)
                p = mp.Process(
                    target=self.handle_glove_conn,
                    args=(
                        conn,
                        self.glove_in_queue[player],
                        self.glove_out_queue[player],
                        player,
                        component,
                    ),
                )
                p_ai = mp.Process(
                    target=player_ai.run,
                )
                p.start()
                p_ai.start()


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
        relay_server_process.terminate()
