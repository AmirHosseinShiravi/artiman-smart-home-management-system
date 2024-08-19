import json
import os
import time
from typing import Callable, Any, Dict
from paho.mqtt import client as mqtt_client
import uuid
from django.core.signals import request_finished
from django.dispatch import receiver
import dotenv

dotenv.load_dotenv()


class MQTTManager:
    def __init__(self, broker: str, port: int = 1883, client_id: str = None, username: str = None, password: str = None):
        self.broker = broker
        self.port = port
        self.client_id = client_id or f'python-mqtt-{uuid.uuid4().hex[:8]}'
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, self.client_id, clean_session=False)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.subscriptions: Dict[str, Callable] = {}
        self.FIRST_RECONNECT_DELAY = 1
        self.RECONNECT_RATE = 2
        self.MAX_RECONNECT_COUNT = 12
        self.MAX_RECONNECT_DELAY = 60
    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0 and self.client.is_connected():
            print(f"Connected to MQTT Broker: {self.broker}")
        else:
            print(f"Failed to connect, return code {rc}")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            payload = msg.payload.decode()

        if topic in self.subscriptions:
            callback = self.subscriptions[topic]
            try:
                callback(topic, payload)
            except Exception as e:
                print(f"Error in callback for topic {topic}: {e}")

    def _on_disconnect(self, client, userdata, rc):

        # logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, self.FIRST_RECONNECT_DELAY
        while reconnect_count < self.MAX_RECONNECT_COUNT:
            # logging.info("Reconnecting in %d seconds...", reconnect_delay)
            print("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                # logging.info("Reconnected successfully!")
                return
            except Exception as err:
                # logging.error("%s. Reconnect failed. Retrying...", err)
                pass
            reconnect_delay *= self.RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, self.MAX_RECONNECT_DELAY)
            reconnect_count += 1
        # logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

    def connect(self):
        try:
            if not self.client.is_connected():
                self.client.connect(self.broker, self.port)
                self.client.loop_start()

        except Exception as e:
            print(f"Occur error when making connection to MQTT broker with error:: {e}")

    def disconnect(self):
        if self.client.is_connected():
            self.client.loop_stop()
            self.client.disconnect()

    def publish(self, topic: str, message: Any):
        if not self.client.is_connected():
            raise ConnectionError("Not connected to MQTT broker")
        payload = json.dumps(message).encode()
        result = self.client.publish(topic, payload)
        status = result[0]
        if status == 0:
            print(f"Message sent to topic {topic}")
        else:
            print(f"Failed to send message to topic {topic}")

    def subscribe(self, topic: str, callback: Callable):
        if not self.client.is_connected():
            raise ConnectionError("Not connected to MQTT broker")
        self.client.subscribe(topic)
        self.subscriptions[topic] = callback
        print(f"Subscribed to topic: {topic}")


# Usage in Django
mqtt_manager = None


def initialize_mqtt():
    global mqtt_manager
    emqx_broker_tcp_host = os.environ.get('emqx_broker_tcp_host')
    emqx_broker_tcp_port = int(os.environ.get('emqx_broker_tcp_port'))
    dashboard_mqtt_username = os.environ.get('dashboard_mqtt_username')
    dashboard_mqtt_password = os.environ.get('dashboard_mqtt_password')

    mqtt_manager = MQTTManager(broker=emqx_broker_tcp_host,
                               port=emqx_broker_tcp_port,
                               client_id="amir",
                               username=dashboard_mqtt_username,
                               password=dashboard_mqtt_password)
    mqtt_manager.connect()


@receiver(request_finished)
def close_mqtt_connection(sender, **kwargs):
    global mqtt_manager
    if mqtt_manager:
        mqtt_manager.disconnect()


def publish_message(topic: str, message: Any):
    global mqtt_manager
    try:
        if mqtt_manager is None:
            raise RuntimeError("MQTT Manager not initialized")
        elif not mqtt_manager.client.is_connected():
            raise RuntimeError("MQTT Manager not connected to broker")
        mqtt_manager.publish(topic, message)
    except Exception as e:
        print(f"Have error while publishing mqtt message with error:: {e}")


def subscribe_to_topic(topic: str, callback: Callable):
    global mqtt_manager
    try:
        if mqtt_manager is None:
            raise RuntimeError("MQTT Manager not initialized")
        elif not mqtt_manager.client.is_connected() :
            raise RuntimeError("MQTT Manager not connected to broker")
        else:
            mqtt_manager.subscribe(topic, callback)
    except Exception as e:
        print(f"Have error while subscribing mqtt topic with error:: {e}")



