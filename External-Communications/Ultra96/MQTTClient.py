import json

import paho.mqtt.client as paho
from paho import mqtt
from paho.mqtt.packettypes import PacketTypes


class MQTTClient:
    def __init__(self, vis_queue, opp_in_frames):
        def on_publish(client, userdata, mid, properties=None):
            print("mid: " + str(mid))

        def on_message(client, userdata, msg):
            msg_data = str(msg.payload.decode("utf-8"))
            print(msg.topic + "  " + msg_data)
            msg_json = json.loads(msg_data)

            index = 0 if msg_json["opp"] == "p1" else 1

            with self.opp_in_frames.get_lock():
                self.opp_in_frames[index] = int(msg_json["inFrame"])
                print(self.opp_in_frames[:])

        self.vis_queue = vis_queue
        self.opp_in_frames = opp_in_frames

        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_message = on_message
        self.client.on_publish = on_publish

        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("cg4002b13", "xilinxB13capstone")
        self.client.connect("c14f3e809cb145569a13b7912611d549.s2.eu.hivemq.cloud", 8883)
        self.client.subscribe("LaserTag/OppInFrame", qos=1)

    def publish(self, data):
        self.client.publish("LaserTag/GameState", data, qos=1)

    def run(self):
        self.client.loop_start()
        while True:
            vis_data = self.vis_queue.get()
            vis_json = json.dumps(vis_data)
            self.publish(vis_json)

    def stop(self):
        self.client.loop_stop()


if __name__ == "__main__":
    mqtt_client = MQTTClient()
    mqtt_client.run()
