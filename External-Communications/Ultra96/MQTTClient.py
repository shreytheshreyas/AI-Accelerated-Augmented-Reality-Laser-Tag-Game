import json
import multiprocessing as mp

import paho.mqtt.client as paho
from paho import mqtt

from Test import put_queue


class MQTTClient:
    def __init__(self, vis_queue, opp_in_frames, logs_queue):
        def on_publish(client, userdata, mid, properties=None):
            self.logs_queue.put("mid: " + str(mid))

        def on_message(client, userdata, msg):
            msg_data = str(msg.payload.decode("utf-8"))
            # self.logs_queue.put(msg.topic + "  " + msg_data)
            msg_json = json.loads(msg_data)

            index = 0 if msg_json["opp"] == "p1" else 1

            with self.opp_in_frames.get_lock():
                if self.opp_in_frames[index] != int(msg_json["inFrame"]):
                    self.opp_in_frames[index] = int(msg_json["inFrame"])
                    self.logs_queue.put(
                        f"OppInFrame updated - p1: {bool(self.opp_in_frames[0])} p2: {bool(self.opp_in_frames[1])}\r"
                    )

        self.vis_queue = vis_queue
        self.opp_in_frames = opp_in_frames
        self.logs_queue = logs_queue

        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_message = on_message
        self.client.on_publish = on_publish

        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("cg4002b13", "xilinxB13capstone")
        self.client.connect("c14f3e809cb145569a13b7912611d549.s2.eu.hivemq.cloud", 8883)
        self.client.subscribe("LaserTag/OppInFrame", qos=1)

    def publish(self, data):
        self.client.publish("LaserTag/GameState", data, qos=1)

    def _run(self):
        self.client.loop_start()
        while True:
            vis_data = self.vis_queue.get()
            vis_json = json.dumps(vis_data)
            self.publish(vis_json)

    def stop(self):
        self.client.loop_stop()

    def run(self):
        try:
            self.logs_queue.put("MQTT Client Started")
            self._run()
        except KeyboardInterrupt:
            self.logs_queue.put("MQTT Client Ended")


if __name__ == "__main__":
    vis_data = [
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

    vis_queue = mp.Queue()
    opp_in_frames = mp.Array("i", [0] * 2)

    mqtt_client = MQTTClient(vis_queue, opp_in_frames)
    mqtt_process = mp.Process(target=mqtt_client.run)
    vis_process = mp.Process(
        target=put_queue,
        args=(
            vis_queue,
            vis_data,
        ),
    )

    try:
        mqtt_process.start()
        vis_process.start()
        mqtt_process.join()
        vis_process.join()

    finally:
        mqtt_process.terminate()
        vis_process.terminate()
