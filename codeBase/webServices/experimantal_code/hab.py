# import asyncio
# from HABApp.core.items import Item
# from HABApp.core.internals import EventBus, Event
# from HABApp.openhab.items import OpenhabItem
#
# # Create an event bus
# event_bus = EventBus()
#
# # Create an item registry
# class ItemRegistry:
#     def __init__(self):
#         self.items = {}
#
#     def add_item(self, item):
#         self.items[item.name] = item
#
#     def get_item(self, name):
#         return self.items.get(name)
#
# item_registry = ItemRegistry()
#
# # Example event handler
# def handle_event(event):
#     print(f"Received event: {event}")
#
# # Subscribe to events
# event_bus.subscribe(Event, handle_event)
#
# # Create and add items
# switch = OpenhabItem("MySwitch", "Switch")
# item_registry.add_item(switch)
#
# # Function to simulate item state change
# def change_item_state(item_name, new_state):
#     item = item_registry.get_item(item_name)
#     if item:
#         item.set_value(new_state)
#         event = Event(f"{item_name} changed to {new_state}")
#         event_bus.post_event(event)
#
# # Main loop
# async def main():
#     while True:
#         # Simulate item state change
#         await asyncio.sleep(5)
#         change_item_state("MySwitch", "ON")
#         await asyncio.sleep(5)
#         change_item_state("MySwitch", "OFF")
#
# # Run the main loop
# asyncio.run(main())