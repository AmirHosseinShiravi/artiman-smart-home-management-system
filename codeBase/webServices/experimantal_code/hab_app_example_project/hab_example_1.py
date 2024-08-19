import datetime
import random

import HABApp
from HABApp.mqtt.items import MqttItem
from HABApp.core.events import ValueChangeEvent, ValueChangeEventFilter, ValueUpdateEvent, ValueUpdateEventFilter


class ExampleMqttTestRule(HABApp.Rule):
    def __init__(self):
        super().__init__()

        # self.run.every(
        #     start_time=datetime.timedelta(seconds=60),
        #     interval=datetime.timedelta(seconds=30),
        #     callback=self.publish_rand_value
        # )
        #
        # # this will trigger every time a message is received under "test/test"
        # self.listen_event('test/test', self.topic_updated, ValueUpdateEventFilter())
        #
        # # This will create an item which will store the payload of the topic so it can be accessed later.
        # self.item = MqttItem.get_create_item('test/value_stored')
        # # Since the payload is now stored we can trigger only if the value has changed
        # self.item.listen_event(self.item_topic_updated, ValueChangeEventFilter())

    def publish_rand_value(self):
        print('test mqtt_publish')
        self.mqtt.publish('test/test', str(random.randint(0, 1000)))

    def topic_updated(self, event: ValueUpdateEvent):
        assert isinstance(event, ValueUpdateEvent), type(event)
        print( f'mqtt topic "test/test" updated to {event.value}')

    def item_topic_updated(self, event: ValueChangeEvent):
        print(self.item.value)  # will output the current item value
        print( f'mqtt topic "test/value_stored" changed from {event.old_value} to {event.value}')


# ExampleMqttTestRule()