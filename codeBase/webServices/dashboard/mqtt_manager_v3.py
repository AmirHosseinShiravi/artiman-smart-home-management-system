import json
import os
import time
from typing import Callable, Any
from paho.mqtt import client as mqtt_client
import uuid
import dotenv
from django.core.signals import request_finished
from django.dispatch import receiver
from django.apps import AppConfig

dotenv.load_dotenv()

class MQTTManager:
    def __init__(self, broker: str, port: int = 1883, username: str = None, password: str = None,
                 transport: str = "tcp", websocket_path: str = "/mqtt"):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.transport = transport
        self.websocket_path = websocket_path
        self.client = None
        self.subscriptions = {}
        self.FIRST_RECONNECT_DELAY = 1
        self.RECONNECT_RATE = 2
        self.MAX_RECONNECT_COUNT = 12
        self.MAX_RECONNECT_DELAY = 60

    def _create_client(self):
        worker_id = os.getpid()
        client_id = f'dashboard-mqtt-{worker_id}-{uuid.uuid4().hex[:8]}'
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id, clean_session=False, transport=self.transport)
        client.username_pw_set(self.username, self.password)
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.on_disconnect = self._on_disconnect
        if self.transport == "websockets":
            client.ws_set_options(path=self.websocket_path)
        return client

    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print(f"Worker {os.getpid()} connected to MQTT Broker: {self.broker}")
            # Resubscribe to topics
            for topic in self.subscriptions:
                client.subscribe(topic)
        else:
            print(f"Worker {os.getpid()} failed to connect, return code {rc}")

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
        print(f"Worker {os.getpid()} disconnected with result code: {rc}")
        self._reconnect()

    def _reconnect(self):
        reconnect_count, reconnect_delay = 0, self.FIRST_RECONNECT_DELAY
        while reconnect_count < self.MAX_RECONNECT_COUNT:
            print(f"Worker {os.getpid()} reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)

            try:
                self.client.reconnect()
                print(f"Worker {os.getpid()} reconnected successfully!")
                return
            except Exception as err:
                print(f"Worker {os.getpid()}: {err}. Reconnect failed. Retrying...")
            reconnect_delay *= self.RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, self.MAX_RECONNECT_DELAY)
            reconnect_count += 1
        print(f"Worker {os.getpid()}: Reconnect failed after {reconnect_count} attempts. Exiting...")

    def connect(self):
        if not self.client:
            self.client = self._create_client()
        if not self.client.is_connected():
            try:
                self.client.connect(self.broker, self.port)
                self.client.loop_start()
            except Exception as e:
                print(f"Worker {os.getpid()}: Error when making connection to MQTT broker: {e}")

    def disconnect(self):
        if self.client and self.client.is_connected():
            self.client.loop_stop()
            self.client.disconnect()

    def publish(self, topic: str, message: Any):
        if not self.client or not self.client.is_connected():
            self.connect()
        payload = json.dumps(message).encode()
        result = self.client.publish(topic, payload)
        status = result[0]
        if status == 0:
            print(f"Worker {os.getpid()}: Message sent to topic {topic}")
        else:
            print(f"Worker {os.getpid()}: Failed to send message to topic {topic}")

    def subscribe(self, topic: str, callback: Callable):
        if not self.client or not self.client.is_connected():
            self.connect()
        self.client.subscribe(topic)
        self.subscriptions[topic] = callback
        print(f"Worker {os.getpid()}: Subscribed to topic: {topic}")

class MQTTAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app_name'

    def ready(self):
        # if os.environ.get('RUN_MAIN', None) != 'true':
        emqx_broker_host = os.environ.get('emqx_broker_host')
        emqx_broker_port = int(os.environ.get('emqx_broker_port'))
        emqx_broker_ws_path = os.environ.get('emqx_broker_ws_path')
        emqx_broker_transport = os.environ.get('emqx_broker_transport')
        dashboard_mqtt_username = os.environ.get('dashboard_mqtt_username')
        dashboard_mqtt_password = os.environ.get('dashboard_mqtt_password')

        self.mqtt_manager = MQTTManager(
            broker=emqx_broker_host,
            port=emqx_broker_port,
            username=dashboard_mqtt_username,
            password=dashboard_mqtt_password,
            transport=emqx_broker_transport,
            websocket_path=emqx_broker_ws_path
        )

        # Establish the connection when the app is ready
        self.mqtt_manager.connect()

        @receiver(request_finished)
        def close_mqtt_connection(sender, **kwargs):
            self.mqtt_manager.disconnect()

# Usage functions
def get_mqtt_manager():
    return MQTTAppConfig.mqtt_manager

def publish_message(topic: str, message: Any):
    mqtt_manager = get_mqtt_manager()
    try:
        mqtt_manager.publish(topic, message)
    except Exception as e:
        print(f"Error while publishing MQTT message: {e}")

def subscribe_to_topic(topic: str, callback: Callable):
    mqtt_manager = get_mqtt_manager()
    try:
        mqtt_manager.subscribe(topic, callback)
    except Exception as e:
        print(f"Error while subscribing to MQTT topic: {e}")