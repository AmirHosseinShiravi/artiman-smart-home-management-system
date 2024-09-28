import json
import os
import time
from typing import Callable, Any, Dict, Literal
from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import MQTTProtocolVersion
import uuid
from django.core.signals import request_finished
from django.dispatch import receiver
import dotenv
from queue import Queue
import threading

dotenv.load_dotenv()


class MQTTManager:
    def __init__(self, broker: str, port: int = 1883, client_id: str = None, username: str = None, password: str = None,
                 transport: Literal["tcp", "websockets", "unix"] = "tcp", websocket_path: str = "/mqtt"):
        self.broker = broker
        self.port = port
        self.client_id = client_id or f'python-mqtt-{uuid.uuid4().hex[:8]}'
        self.transport = transport
        self.websocket_path = websocket_path
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2,
                                         self.client_id,
                                         clean_session=None,
                                         protocol=MQTTProtocolVersion.MQTTv5,
                                         transport=self.transport)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.subscriptions: Dict[str, Callable] = {}
        self.FIRST_RECONNECT_DELAY = 1
        self.RECONNECT_RATE = 2
        self.MAX_RECONNECT_COUNT = 12
        self.MAX_RECONNECT_DELAY = 60
        self.command_queue = Queue()
        self.is_processing_queue = False
        self.process_queue_thread = None


    def _process_queue(self):
        self.is_processing_queue = True
        while not self.command_queue.empty():
            command, args = self.command_queue.get()
            if command == 'publish':
                topic, message = args
                self.publish(topic, message)
            elif command == 'subscribe':
                topic, callback = args
                self.subscribe(topic, callback)
            self.command_queue.task_done()
        self.is_processing_queue = False


    def _on_connect(self, client, userdata, reason_code, properties, rc):
        if self.client.is_connected():
            print(f"Connected to MQTT Broker: {self.broker}")
            if not self.process_queue_thread or not self.process_queue_thread.is_alive():
                self.process_queue_thread = threading.Thread(target=self._process_queue)
                self.process_queue_thread.start()
        else:
            print(f"Failed to connect, return code {reason_code}")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            payload = msg.payload.decode()

        if any(self.topic_matches(subscribed_topic, topic) for subscribed_topic in self.subscriptions):
            matching_topics = [st for st in self.subscriptions if self.topic_matches(st, topic)]
            for matching_topic in matching_topics:
                callback = self.subscriptions[matching_topic]
                try:
                    callback(topic, payload)
                except Exception as e:
                    print(f"Error in callback for topic {topic}: {e}")

                    
    def topic_matches(self, subscribed_topic, published_topic):
        sub_parts = subscribed_topic.split('/')
        pub_parts = published_topic.split('/')

        # If the subscribed topic ends with '#', it matches the rest of the published topic
        if sub_parts[-1] == '#':
            return len(pub_parts) >= len(sub_parts) - 1 and all(
                part == '+' or part == pub_parts[i]
                for i, part in enumerate(sub_parts[:-1])
            )

        # Otherwise, the number of parts should be the same
        if len(sub_parts) != len(pub_parts):
            return False

        # Check each part
        return all(
            sub_part == '+' or sub_part == pub_part
            for sub_part, pub_part in zip(sub_parts, pub_parts)
        )


    def _on_disconnect(self, client, userdata, reason_code, properties, rc):

        print(f"Disconnected with result code: {reason_code}")
        reconnect_count, reconnect_delay = 0, self.FIRST_RECONNECT_DELAY
        while reconnect_count < self.MAX_RECONNECT_COUNT:
            # logging.info("Reconnecting in %d seconds...", reconnect_delay)
            print(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                print("Reconnected successfully!")
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
                if self.transport == "websockets":
                    self.client.ws_set_options(path=self.websocket_path)
                self.client.connect(self.broker, self.port)
                self.client.loop_start()
        except Exception as e:
            print(f"Occur error when making connection to MQTT broker with error:: {e}")

    def disconnect(self):
        if self.client.is_connected():
            self.client.loop_stop()
            self.client.disconnect()


    def publish(self, topic: str, message: Any, retain: bool = False, qos: int = 0):
        if not self.client.is_connected():
            raise ConnectionError("Not connected to MQTT broker")
        payload = str(message).encode()
        result = self.client.publish(topic, payload, qos=qos, retain=retain)
        status = result[0]
        if status == 0:
            print(f"Message sent to topic {topic}")
        else:
            print(f"Failed to send message to topic {topic}")
            self.command_queue.put(('publish', (topic, message, retain, qos)))
            print(f"Client not connected. Queued publish command for topic: {topic}")


    def subscribe(self, topic: str, callback: Callable):
        try:
            if not self.client.is_connected():
                self.command_queue.put(('subscribe', (topic, callback)))
                print(f"Client not connected. Queued subscribe command for topic: {topic}")
                raise ConnectionError("Not connected to MQTT broker")
            self.client.subscribe(topic)
            self.subscriptions[topic] = callback
            print(f"Subscribed to topic: {topic}")
        except Exception as e:
            print(f"exception in subscribe method:: error: {e}")

    # write a method to unsubscribe from a topic
    def unsubscribe(self, topic: str):
        if topic in self.subscriptions:
            self.client.unsubscribe(topic)
            del self.subscriptions[topic]
            print(f"Unsubscribed from topic: {topic}")
        else:
            print(f"Not subscribed to topic: {topic}")


# Usage in Django
mqtt_manager = None


def initialize_mqtt():
    global mqtt_manager
    emqx_broker_host = os.environ.get('emqx_broker_host')
    emqx_broker_port = int(os.environ.get('emqx_broker_port'))
    emqx_broker_ws_path = os.environ.get('emqx_broker_ws_path')
    emqx_broker_transport = os.environ.get('emqx_broker_transport')
    dashboard_mqtt_client_id = os.environ.get('dashboard_mqtt_clientId')
    dashboard_mqtt_username = os.environ.get('dashboard_mqtt_username')
    dashboard_mqtt_password = os.environ.get('dashboard_mqtt_password')

    mqtt_manager = MQTTManager(broker=emqx_broker_host,
                               port=emqx_broker_port,
                               client_id=dashboard_mqtt_client_id,
                               username=dashboard_mqtt_username,
                               password=dashboard_mqtt_password,
                               transport=emqx_broker_transport,
                               websocket_path=emqx_broker_ws_path)
    mqtt_manager.connect()



# @receiver(request_finished)
def close_mqtt_connection(sender, **kwargs):
    global mqtt_manager
    if mqtt_manager:
        mqtt_manager.disconnect()
        print("MQTT connection closed")


def publish_message(topic: str, message: Any, retain: bool = False, qos: int = 0):
    global mqtt_manager
    try:
        if mqtt_manager is None:
            raise RuntimeError("MQTT Manager not initialized")
        # elif not mqtt_manager.client.is_connected():
        #     raise RuntimeError("MQTT Manager not connected to broker")
        mqtt_manager.publish(topic, message, retain, qos)
    except Exception as e:
        print(f"Have error while publishing mqtt message with error:: {e}")


def subscribe_to_topic(topic: str, callback: Callable):
    global mqtt_manager
    try:
        if mqtt_manager is None:
            raise RuntimeError("MQTT Manager not initialized")
        # elif not mqtt_manager.client.is_connected() :
        #     raise RuntimeError("MQTT Manager not connected to broker")
        else:
            mqtt_manager.subscribe(topic, callback)
    except Exception as e:
        print(f"Have error while subscribing mqtt topic with error:: {e}")

def unsubscribe_from_topic(topic: str):
    global mqtt_manager
    try:
        if mqtt_manager is None:
            raise RuntimeError("MQTT Manager not initialized")
        else:
            mqtt_manager.unsubscribe(topic)
    except Exception as e:
        print(f"Have error while unsubscribing mqtt topic with error:: {e}")

