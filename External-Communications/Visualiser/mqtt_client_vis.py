import time

import paho.mqtt.client as paho
from paho import mqtt


class MQTT_Client:
    def __init__(self):
        def on_publish(client, userdata, mid, properties=None):
            print("mid: " + str(mid))

        def on_message(client, userdata, msg):
            print(msg.topic + "  " + str(msg.payload))

        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_message = on_message
        self.client.on_publish = on_publish

        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set("cg4002b13", "xilinxB13capstone")

        self.client.connect("c14f3e809cb145569a13b7912611d549.s2.eu.hivemq.cloud", 8883)
        print("Connected to MQTT server")
        self.client.subscribe("LaserTag/GameState", qos=1)

    def run(self):
        self.client.loop_start()
        inFrame = True
        while True:
            time.sleep(5)
            if inFrame:
                self.client.publish(
                    "LaserTag/OppInFrame", '{"opp": "p1", "inFrame": true}', qos=1
                )
            else:
                self.client.publish(
                    "LaserTag/OppInFrame", '{"opp": "p1", "inFrame": false}', qos=1
                )
            inFrame = not inFrame


if __name__ == "__main__":
    mqtt_client = MQTT_Client()
    mqtt_client.run()
