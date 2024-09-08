# import json
# import os
# from typing import Callable, Any, Dict
# from paho.mqtt import client as mqtt_client
# import uuid
#
#
# class MQTTManager:
#     _instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             cls._instance = super(MQTTManager, cls).__new__(cls)
#         return cls._instance
#
#     def __init__(self, broker: str, port: int = 1883, client_id: str = None, username: str = None, password: str = None):
#         if not hasattr(self, 'initialized'):
#             self.broker = broker
#             self.port = port
#             self.client_id = client_id or f'python-mqtt-{uuid.uuid4().hex[:8]}'
#             self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, self.client_id, clean_session=False)
#             self.client.username_pw_set(username, password)
#             self.client.on_connect = self._on_connect
#             self.client.on_message = self._on_message
#             self.subscriptions: Dict[str, Callable] = {}
#             self.is_connected = False
#             self.initialized = True
#
#     def _on_connect(self, client, userdata, flags, rc, properties):
#         if rc == 0:
#             print(f"Connected to MQTT Broker: {self.broker}")
#             self.is_connected = True
#         else:
#             print(f"Failed to connect, return code {rc}")
#             self.is_connected = False
#
#     def _on_message(self, client, userdata, msg):
#         topic = msg.topic
#         try:
#             payload = json.loads(msg.payload.decode())
#         except json.JSONDecodeError:
#             payload = msg.payload.decode()
#
#         if topic in self.subscriptions:
#             callback = self.subscriptions[topic]
#             try:
#                 callback(topic, payload)
#             except Exception as e:
#                 print(f"Error in callback for topic {topic}: {e}")
#
#     def connect(self):
#         if not self.is_connected:
#             self.client.connect(self.broker, self.port)
#             self.client.loop_start()
#
#     def disconnect(self):
#         if self.is_connected:
#             self.client.loop_stop()
#             self.client.disconnect()
#             self.is_connected = False
#
#     def publish(self, topic: str, message: Any):
#         if not self.is_connected:
#             raise ConnectionError("Not connected to MQTT broker")
#         payload = json.dumps(message).encode()
#         result = self.client.publish(topic, payload)
#         status = result[0]
#         if status == 0:
#             print(f"Message sent to topic {topic}")
#         else:
#             print(f"Failed to send message to topic {topic}")
#
#     def subscribe(self, topic: str, callback: Callable):
#         if not self.is_connected:
#             raise ConnectionError("Not connected to MQTT broker")
#         self.client.subscribe(topic)
#         self.subscriptions[topic] = callback
#         print(f"Subscribed to topic: {topic}")
#
#
# # Global instance
# emqx_broker_tcp_host = os.environ.get('emqx_broker_tcp_host')
# emqx_broker_tcp_port = int(os.environ.get('emqx_broker_tcp_port'))
# dashboard_mqtt_username = os.environ.get('dashboard_mqtt_username')
# dashboard_mqtt_password = os.environ.get('dashboard_mqtt_password')
#
# mqtt_manager = MQTTManager(broker=emqx_broker_tcp_host,
#                            port=emqx_broker_tcp_port,
#                            client_id="amir",
#                            username=dashboard_mqtt_username,
#                            password=dashboard_mqtt_password)
#
#
# def initialize_mqtt():
#     mqtt_manager.connect()
