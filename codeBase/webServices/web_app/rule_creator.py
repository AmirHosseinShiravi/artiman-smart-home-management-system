import re
import os
import json
import base64
import requests
from pathlib import Path
from jinja2 import Template
from .models import LinkageRule
from core.settings import BASE_DIR
from dashboard.models import Home, HomeUser, Project


class LinkageRuleCreator:
    def __init__(self, rule_uuid):
        self.rule_uuid = rule_uuid
        self.rule_instance = None
        self.home = None
        self.project = None
        if LinkageRule.objects.filter(uuid=rule_uuid).exists():
            self.rule_instance = LinkageRule.objects.get(uuid=rule_uuid)
            self.home = Home.objects.filter(uuid=self.rule_instance.parent_home__uuid).get()
            self.project = Project.objects.filter(uuid=self.rule_instance.parent_project__uuid).get()
        self.rule_config: dict = self.rule_instance.rule_config
        self.rule_code: str = str()

    def create_linkage_rule_file(self):
        # TODO[-]: first check config file to validate it's parameters like validity of controller, home, project,
        #  linkage rule and ... . Maybe, attacker set another home or project uuid's in it's sent linkage config
        #  and wanted access to another project or home.
        self.rule_config["name"] = self.rule_instance.name
        self.rule_config["rule_uuid"] = self.rule_instance.uuid
        self.rule_config["project_uuid"] = self.rule_instance.parent_project.uuid
        self.rule_config["home_uuid"] = self.rule_instance.parent_home.uuid
        template = Template('''
        import re
        import os
        import json
        import pytz
        import HABApp
        from enum import Enum
        from pathlib import Path
        from HABApp.core.items import Item
        from HABApp.mqtt.items import MqttItem
        from datetime import datetime, time, timedelta, date
        from HABApp.core.events import ValueChangeEvent, ValueChangeEventFilter, ValueUpdateEvent, ValueUpdateEventFilter
        from HABApp.core.events.habapp_events import RequestFileLoadEvent

        class ValueTypes(Enum):
            BOOLEAN = 'BOOLEAN'
            INTEGER = 'INTEGER'
            DECIMAL = 'DECIMAL'
            FLOAT = 'FLOAT'
            STRING = 'STRING'
            JSON = 'JSON'
            DATE = 'DATE'
            DATETIME = 'DATETIME'
            TIME = 'TIME'


        class ActionStatus(Enum):
            PENDING = "Pending"
            IN_PROGRESS = "In Progress"
            COMPLETED = "Completed"
            FAILED = "Failed"
            CANCELLED = "Cancelled"

            def __str__(self):
                return self.value


        class LinkageRuleExecutionStatus(Enum):
            ENABLE = "enable"
            DISABLE = "disable"
            # PENDING = "Pending"
            IN_PROGRESS = "In Progress"
            COMPLETED = "Completed"
            FAILED = "Failed"
            # CANCELLED = "Cancelled"

            def __str__(self):
                return self.value


        def value_caster(input_value, output_type):
            try:
                if output_type == ValueTypes.BOOLEAN.value:
                    if isinstance(input_value, str):
                        if input_value.lower() in ['true', '1', 'yes', 'on']:
                            return True
                        elif input_value.lower() in ['false', '0', 'no', 'off']:
                            return False
                        else:
                            return False
                    elif isinstance(input_value, bool):
                        return bool(input_value)

                elif output_type == ValueTypes.INTEGER.value:
                    return int(input_value)

                elif output_type == ValueTypes.DECIMAL.value or output_type == ValueTypes.FLOAT.value:
                    return float(input_value)

                elif output_type == ValueTypes.STRING.value:
                    return str(input_value)

                elif output_type == ValueTypes.JSON.value:
                    if isinstance(input_value, str):
                        return json.loads(input_value)
                    else:
                        return json.dumps(input_value)

                elif output_type == ValueTypes.DATE.value:
                    if isinstance(input_value, str):
                        return datetime.strptime(input_value, '%Y-%m-%d').date()
                    elif isinstance(input_value, datetime):
                        return input_value.date()
                    return input_value

                elif output_type == ValueTypes.TIME.value:
                    if isinstance(input_value, str):
                        return datetime.strptime(input_value, '%H:%M:%S').time()
                    elif isinstance(input_value, time):
                        return input_value
                    return input_value

                elif output_type == ValueTypes.DATETIME.value:
                    if isinstance(input_value, str):
                        return datetime.strptime(input_value, '%Y-%m-%d %H:%M:%S')
                    elif isinstance(input_value, datetime):
                        return input_value
                    return input_value

                else:
                    raise ValueError(f"Unsupported output type: {output_type}")

            except (ValueError, TypeError, json.JSONDecodeError) as e:
                print(f"Error casting value: {e}")
                return None


        def compare_json(json1, json2, comparator):
            if comparator == '==':
                return json1 == json2
            else:
                raise ValueError(f"Comparator '{comparator}' is not supported for JSON data")


        def compare_values(status_value, status_type, item_event_value, item_type, comparator):
            try:
                casted_status_value = value_caster(status_value, status_type)
                casted_item_event_value = value_caster(item_event_value, item_type)

                if casted_status_value is None or casted_item_event_value is None:
                    print("Error in casting values. Comparison not possible.")
                    return None

                if status_type == ValueTypes.JSON.value or item_type == ValueTypes.JSON.value:
                    return compare_json(casted_status_value, casted_item_event_value, comparator)

                if comparator == '==':
                    return casted_status_value == casted_item_event_value
                elif comparator == '>':
                    return casted_status_value > casted_item_event_value
                elif comparator == '<':
                    return casted_status_value < casted_item_event_value
                else:
                    raise ValueError(f"Unsupported comparator: {comparator}")
            except Exception as e:
                print(f"Error occur in compare_value function with error:: {e}")
                return False


        class LinkageRule(HABApp.Rule):
            def __init__(self, linkage_rule_config):
                super().__init__()
                self.config: dict = linkage_rule_config
                self.linkage_rule_type: str = 'scene'
                self.rule_uuid: str | None = None
                self.project_uuid = self.config.get('project_uuid')
                self.home_uuid = self.config.get('home_uuid')
                self.linkage_rule_base_topic = ""
                self.param_file_name: str = ''
                self.decision_expr: str = 'or'
                self.effective_time: dict = {
                    "start": "00:00:00",
                    "end": "23:59:59",
                    "loops": "1111111",
                    "timezone_id": "Asia/Tehran"
                }
                self.condition_event_listeners: dict[int, MqttItem.listen_event] = dict()
                self.actions: list = []
                self.actions_status: dict[int:Item] = {}
                self.conditions: list = []
                self.conditions_status: dict = {}
                self.linkage_rule_execution_status = None
                self.tap_to_run_command_status: bool = False
                self.listeners = None
                self.create_rule()
                self.create_action()

            def create_rule(self):
                # Extract details from config
                self.rule_name = self.config.get('name')
                self.rule_uuid = self.config.get('rule_uuid')
                self.linkage_rule_base_topic = f"v1/projects/{self.project_uuid}/homes/{self.home_uuid}/linkage-rules/{self.rule_uuid}"
                self.linkage_rule_type = self.config.get('type', 'scene')
                self.decision_expr = self.config.get('decision_expr', "or")
                self.effective_time = self.config.get('effective_time', self.effective_time)
                self.conditions = self.config.get('conditions', [])
                self.actions = self.config.get('actions', [])
                self.param_file_name = f"rule_params_{self.rule_uuid}"

                if self.linkage_rule_type == "scene":
                    self.tap_to_run_status_item = MqttItem.get_create_item(name=self.linkage_rule_base_topic + "/actions/trigger/")
                    # print("Tap-to-run topic:: " + self.tap_to_run_status_item.name)
                    self.tap_to_run_status_item.listen_event(self.tap_to_run_execute_actions, ValueUpdateEventFilter())

                elif self.linkage_rule_type == "automation":
                    # Create condition and action handlers
                    # If first condition was device report and last stored value in parameter file is not equal to new retained
                    # value, 'evaluate_device_report' and 'make_decision_based_on_conditions' were called and because only
                    # one of conditions will be registered, 'make_decision_based_on_conditions' function deside to run
                    # execute_actions function and this behavior is wrong. So at the first, we declare and initialize
                    # 'conditions_status' dictionary and in separate for loop, call 'create_condition' to create all conditions.
                    for condition in self.conditions:
                        condition_code = int(condition["code"])
                        self.conditions_status[condition_code] = False

                    for condition in self.conditions:
                        self.create_condition(condition)
                else:
                    print(f"rule type not supported")

                # f"v1/linkage-rules/{self.rule_uuid}/status/get" values:: 'enable' - 'disable' - 'in-progress' - 'completed'
                # f"v1/linkage-rules/{self.rule_uuid}/status/set" values:: 'enable' - 'disable'
                # add linkage rule status event listener
                self.linkage_rule_execution_set_status_item = MqttItem.get_create_item(self.linkage_rule_base_topic + "/status/set")
                self.linkage_rule_execution_set_status_item.listen_event(self.set_rule_execution_status, ValueUpdateEventFilter())

                item_name = self.linkage_rule_base_topic + "/status/get"
                item_new_name = item_name.replace("/", "\/")
                self.linkage_rule_execution_status = Item.get_create_item(name=item_new_name)

                self.linkage_rule_execution_status.listen_event(callback=self.get_rule_execution_status, event_filter=ValueChangeEventFilter())
                self.linkage_rule_execution_status.post_value(LinkageRuleExecutionStatus.ENABLE)

            def set_rule_execution_status(self, event: ValueUpdateEvent):
                if event.value == LinkageRuleExecutionStatus.ENABLE.value:
                    self.linkage_rule_execution_status.post_value(LinkageRuleExecutionStatus.ENABLE)
                elif event.value == LinkageRuleExecutionStatus.DISABLE.value:
                    self.linkage_rule_execution_status.post_value(LinkageRuleExecutionStatus.DISABLE)
                else:
                    self.linkage_rule_execution_status.post_value(LinkageRuleExecutionStatus.ENABLE)

            def get_rule_execution_status(self, event: ValueChangeEvent):
                topic = event.name.replace('\/', '/')
                self.mqtt.publish(topic, payload=str(event.value), qos=2, retain=True)

            def create_condition(self, condition):
                entity_type = condition['entity_type']
                expr = condition['expr']
                condition_code = int(condition["code"])
                # Example: Listen to item state changes
                if entity_type == "device_report":
                    controller_uuid = condition['controller_uuid']
                    device_uuid = condition['device_uuid']
                    data_point_function_name = expr['status_code']

                    mqtt_item_name = f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get"

                    last_value_of_mqtt_item = None
                    try:
                        last_value_of_mqtt_item = HABApp.Parameter(self.param_file_name, "last_value_of_" + mqtt_item_name, default_value=None)
                        # if parameter not exist, raise an exception by getting its value
                        __value_fdfdfdf = last_value_of_mqtt_item.value
                    except FileNotFoundError as e:
                        print(f"Rule param file not found, Error:: {e}")
                        last_value_of_mqtt_item = HABApp.Parameter(self.param_file_name, "last_value_of_" + mqtt_item_name, default_value="not_initialized")
                    except Exception as e:
                        print(f"item does not found in parameter file. Error:: {e}")
                        last_value_of_mqtt_item = HABApp.Parameter(self.param_file_name, "last_value_of_" + mqtt_item_name, default_value="not_initialized")


                    # Because when HABApp engine run before running rules in rules folder, internal mqtt listener get retained
                    # topic messages but when it wanted to call item event listener, faced with empty listener and below
                    # listeners not registered in item event bus, so event not fired and  "evaluate_device_report_conditions"
                    # callback function not called successfully. For fixing this problem I work a few hours but can not fix it,
                    # so I decide to fix it manually to find better solution at future.
                    # try:
                    #     # if item does not exist, raise an "HABApp.core.errors.ItemNotFoundException" exception.
                    #     item = MqttItem.get_item(mqtt_item_name)
                    #
                    #     # call callback manually
                    #     # don't call callback for retain items because it might near to 100%, habapp crash not overlap to device
                    #     # report message and retain messages only usable for front-end usage. if we
                    #     # self.evaluate_device_report_conditions(event=ValueUpdateEvent(name=item.name, value=item.value))
                    # # except HABApp.core.errors.ItemNotFoundException as e:
                    # except Exception as e:
                    #     print(f"not found device_report item and get error:: {e} :: error type::  {type(e)}")
                    #     item = MqttItem.get_create_item(f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get")
                    #     print(f"mqtt item value:: {item.value}")
                    #     item_listener = item.listen_event(self.evaluate_device_report_conditions, ValueUpdateEventFilter())

                    # self.condition_event_listeners[condition_code] = item_listener
                    # self.listen_event(f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get", self.evaluate_device_report_conditions, ValueUpdateEventFilter())
                    # self.post_event(f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get", ValueUpdateEvent(name=f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get" ,value='on'))
                    # SUBSCRIPTION_HANDLER.apply_subscriptions()

                    self.___item = MqttItem.get_create_item(f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get")
                    print(f"mqtt item value:: {self.___item.value}")
                    item_listener = self.___item.listen_event(self.evaluate_device_report_conditions_with_calling_make_decision, ValueUpdateEventFilter())
                    if last_value_of_mqtt_item.value is not None and last_value_of_mqtt_item.value != "not_initialized" and self.___item.value != None:
                        if self.___item.value != last_value_of_mqtt_item.value:
                            self.evaluate_device_report_conditions(event=ValueUpdateEvent(name=self.___item.name, value=self.___item.value))
                            self.make_decision_based_on_conditions()
                        else:
                            self.evaluate_device_report_conditions(event=ValueUpdateEvent(name=self.___item.name, value=self.___item.value))

                elif entity_type == "timer":
                    expr = condition['expr']
                    condition_code = int(condition["code"])
                    desire_date = expr.get("date", None)
                    desire_time = expr.get("time", None)

                    if desire_date is not None:
                        if isinstance(expr["date"], str) and expr["date"].strip():
                            desire_date = value_caster(expr["date"], ValueTypes.DATE.value)
                            print(f"desire_date:: {desire_date}. type:: {type(desire_date)}")

                    if desire_time is not None:
                        if isinstance(expr["time"], str) and expr["time"].strip():
                            desire_time = value_caster(desire_time, ValueTypes.TIME.value)

                    # Iso weekday
                    # Integer Returned     Day of the week
                    #         1               Monday
                    #         2               Tuesday
                    #         3               Wednesday
                    #         4               Thursday
                    #         5               Friday
                    #         6               Saturday
                    #         7               Sunday
                    loops = expr["loops"]
                    days_of_week = []
                    for index, i in enumerate(str(loops).strip(), start=1):
                        if int(i) == 1:
                            days_of_week.append(index)

                    timezone_id = expr["timezone_id"]

                    # if date set in condition, means rule must be checked only in one day(day of making rule)
                    if isinstance(desire_date, date) and isinstance(desire_time, time):
                        local_timezone = pytz.timezone('Asia/Tehran')
                        # Combine date and time into a datetime object
                        combined_datetime = datetime.combine(desire_date, desire_time)
                        # Localize the datetime object to the specified time zone
                        local_datetime_with_tz = local_timezone.localize(combined_datetime)
                        # Convert the localized datetime to UTC
                        utc_datetime = local_datetime_with_tz.astimezone(pytz.utc)
                        print(f"date:: utc_datetime:: {utc_datetime}")
                        self.run.at(utc_datetime, self.evaluate_timer_conditions, condition_code=condition_code)

                    # if loops and time will be set, means user wants to check this condition regularly
                    elif len(days_of_week) > 0 and isinstance(desire_time, time):
                        # print(days_of_week)
                        # print(_local_timezone())
                        local_timezone = pytz.timezone('Asia/Tehran')
                        # Combine the time with an arbitrary date (e.g., today's date)
                        # Note: We use datetime.combine to create a datetime object.
                        local_datetime = datetime.combine(datetime.today(), desire_time)
                        # Localize the datetime object to the specified time zone
                        local_datetime_with_tz = local_timezone.localize(local_datetime)
                        local_time = local_datetime_with_tz.time()

                        a = self.run.on_day_of_week(local_time, weekdays=days_of_week, callback=self.evaluate_timer_conditions, condition_code=condition_code)
                        # print(a._apply_boundaries())
                        print(f"remaining:: {a.remaining()}")
                        # print(a.get_next_run())

                elif entity_type == "weather":
                    pass

            def evaluate_device_report_conditions(self, event: ValueUpdateEvent):
                for condition in self.conditions:
                    if condition["entity_type"] == "device_report":
                        expr = condition['expr']
                        condition_code = int(condition["code"])

                        controller_uuid = condition['controller_uuid']
                        device_uuid = condition['device_uuid']
                        data_point_function_name = expr['status_code']
                        topic = f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get"
                        if topic == event.name:
                            HABApp.Parameter.set_parameter(self.param_file_name, "last_value_of_" + topic, value=event.value)
                            # print(f" Event received with name:: {event.name} by value:: {event.value}")
                            value_type = expr["value_type"]
                            status_value = expr["status_value"]
                            comparator = expr["comparator"]
                            compare_result = compare_values(status_value=status_value,
                                                            status_type=value_type,
                                                            item_event_value=event.value,
                                                            item_type=value_type,
                                                            comparator=comparator)

                            print(f" Event received with name:: {event.name} by value:: {event.value} and value type:: {type(event.value)}"
                                  f"\n compare result:: {compare_result}")

                            if compare_result:
                                self.conditions_status[condition_code] = True

                            else:
                                self.conditions_status[condition_code] = False

            def evaluate_device_report_conditions_with_calling_make_decision(self, event: ValueUpdateEvent):
                for condition in self.conditions:
                    if condition["entity_type"] == "device_report":
                        expr = condition['expr']
                        condition_code = int(condition["code"])

                        controller_uuid = condition['controller_uuid']
                        device_uuid = condition['device_uuid']
                        data_point_function_name = expr['status_code']
                        topic = f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get"
                        if topic == event.name:
                            HABApp.Parameter.set_parameter(self.param_file_name, "last_value_of_" + topic, value=event.value)
                            # print(f" Event received with name:: {event.name} by value:: {event.value}")
                            value_type = expr["value_type"]
                            status_value = expr["status_value"]
                            comparator = expr["comparator"]
                            compare_result = compare_values(status_value=status_value,
                                                            status_type=value_type,
                                                            item_event_value=event.value,
                                                            item_type=value_type,
                                                            comparator=comparator)

                            print(f" Event received with name:: {event.name} by value:: {event.value} and value type:: {type(event.value)}"
                                  f"\n compare result:: {compare_result}")

                            if compare_result:
                                self.conditions_status[condition_code] = True
                                self.make_decision_based_on_conditions()
                            else:
                                self.conditions_status[condition_code] = False
                                self.make_decision_based_on_conditions()
                                return 0

            def evaluate_timer_conditions(self, condition_code):
                self.conditions_status[condition_code] = True
                self.make_decision_based_on_conditions()
                # setting it to False because timer value is no longer valid and time was passed.
                self.conditions_status[condition_code] = False

            def evaluate_weather_conditions(self):
                pass

            def make_decision_based_on_conditions(self):
                if str(self.linkage_rule_execution_status.value) not in [str(LinkageRuleExecutionStatus.DISABLE), str(LinkageRuleExecutionStatus.IN_PROGRESS)]:
                    # for print out all conditions any time any one triggered
                    for condition_code, condition_status in self.conditions_status.items():
                        print(f"condition:: {condition_code} :: status:: {condition_status}")

                    if self.linkage_rule_type == "automation":
                        # check all conditions and if all of them were satisfied, do actions
                        if self.decision_expr == "or":
                            for condition_code, condition_status in self.conditions_status.items():
                                if condition_status is True:
                                    within_allowed_time_frame = self.check_effective_time()
                                    if within_allowed_time_frame:
                                        self.linkage_rule_execution_status.post_value(LinkageRuleExecutionStatus.IN_PROGRESS)
                                        self.execute_actions()
                                    return

                        elif self.decision_expr == "and":
                            number_of_conditions = len(self.conditions_status)
                            satisfied_conditions_counter = 0
                            for condition_code, condition_status in self.conditions_status.items():
                                if condition_status is True:
                                    satisfied_conditions_counter += 1

                            if satisfied_conditions_counter == number_of_conditions:
                                within_allowed_time_frame = self.check_effective_time()
                                if within_allowed_time_frame:
                                    self.linkage_rule_execution_status.post_value(LinkageRuleExecutionStatus.IN_PROGRESS)
                                    self.execute_actions()
                                return
                else:
                    return 0
                return 0

            def get_effective_time_parameters(self):
                start_time = self.effective_time.get("start", None)
                end_time = self.effective_time.get("end", None)
                loops = self.effective_time.get("loops", None)
                if start_time is not None:
                    if isinstance(start_time, str) and start_time.strip():
                        start_time = value_caster(start_time, ValueTypes.TIME.value)
                        # print(f"start_time:: {start_time}. type:: {type(start_time)}")

                if end_time is not None:
                    if isinstance(end_time, str) and end_time.strip():
                        end_time = value_caster(end_time, ValueTypes.TIME.value)

                # Iso weekday
                # Integer Returned     Day of the week
                #         1               Monday
                #         2               Tuesday
                #         3               Wednesday
                #         4               Thursday
                #         5               Friday
                #         6               Saturday
                #         7               Sunday

                days_of_week = []
                for index, i in enumerate(str(loops).strip(), start=1):
                    if int(i) == 1:
                        days_of_week.append(index)

                timezone_id = self.effective_time["timezone_id"]

                return start_time, end_time, days_of_week

            def check_effective_time(self):
                start_time, end_time, days_of_week = self.get_effective_time_parameters()
                # if date set in condition, means rule must be checked only in one day(day of making rule)
                if not isinstance(start_time, time) or  not isinstance(end_time, time) or len(days_of_week) == 0:
                    self.effective_time: dict = {
                        "start": "00:00:00",
                        "end": "23:59:59",
                        "loops": "1111111",
                        "timezone_id": "Asia/Tehran"
                    }
                    start_time, end_time, days_of_week = self.get_effective_time_parameters()
                else:
                    # local_timezone = pytz.timezone('Asia/Tehran')
                    # now = datetime.now(tz=local_timezone)
                    # now_time = now.time()
                    # valid_iso_week_day = []

                    # start_datetime = datetime.now(tz=local_timezone).replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
                    # end_datetime = datetime.now(tz=local_timezone).replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)
                    # if start_time > end_time:
                    #     if now_time > start_time:
                    #         pass
                    #     # time passed from start day and be in tomorrow
                    #     elif now_time < start_time and now_time.hour >= 0:
                    #         pass
                    #     # we should determine we have valid loop value for previous day or not. if we have, it means we are be
                    #     # in previous day valid effective time, but if we haven't valid loop value, it means we are in a time
                    #     # that effective time not started and rule should be waited to reach to start time.
                    #     # For example:
                    #     #   start_time : 23:00
                    #     #   end_time   : 20:00
                    #     #   now(monday): 19:00
                    #     #   condition 1:
                    #     #       loops  : 1000001
                    #     #       in effective time: Yes
                    #     #   condition 2:
                    #     #       loops  : 1000000
                    #     #       in effective time: No
                    #     elif now_time < start_time and now_time < end_time:
                    #         pass
                    #     # be in start day and time not passed from 24 hour
                    #     else:
                    #         pass
                    # # start and end time be in same day
                    # else:
                    #     # we haven't any condition
                    #     pass
                    #
                    # now_iso_week_day = now.isoweekday()
                    # valid_iso_week_day.append(now_iso_week_day)
                    #
                    #
                    # if start_time > end_time:
                    #     end_datetime = end_datetime.replace(day=end_datetime.day + 1)
                    #     valid_iso_week_day.append(end_datetime.isoweekday())
                    #
                    # if start_datetime < now < end_datetime:
                    #     if now_iso_week_day in days_of_week:
                    #         return True
                    #     else:
                    #         return False
                    # else:
                    #     return False
                    now = datetime.now()
                    current_time = now.time()
                    current_weekday = now.isoweekday()
                    # Convert start and end times to time objects
                    start_time = time.fromisoformat(self.effective_time["start"])
                    end_time = time.fromisoformat(self.effective_time["end"])

                    # Check if today is allowed in the loops
                    if self.effective_time["loops"][current_weekday - 1] == '0':
                        return False

                    # Case 1: Start and End on the same day
                    if start_time <= end_time:
                        return start_time <= current_time <= end_time

                    # Case 2: Time span crosses midnight
                    if start_time > end_time:
                        if current_time >= start_time or current_time <= end_time:
                            return True
                        else:
                            if start_time > current_time > end_time:
                                return False
                            else:
                                # Check if the previous day is allowed
                                previous_day = (current_weekday - 2) % 7
                                if self.effective_time["loops"][previous_day] == '1' and current_time <= end_time:
                                    return True

                    return False

            def create_action(self):
                # Prepare action based on executor
                for action in self.actions:
                    action_code = action["code"]
                    item_name = self.linkage_rule_base_topic + f"/actions/actions-status/{action_code}"
                    item_new_name = item_name.replace("/", "\/")
                    self.action_status_item = Item.get_create_item(name=item_new_name)

                    self.action_status_item.listen_event(callback=self.send_action_status, event_filter=ValueChangeEventFilter())
                    self.actions_status[action_code] = self.action_status_item
                    aa = self.action_status_item.post_value(ActionStatus.PENDING)

            def send_action_status(self, event: ValueChangeEvent):
                action_status_topic = event.name.replace('\/', '/')
                match = re.search(r'actions-status/(\d+)', action_status_topic)
                # Extracting the number if a match is found
                if match:
                    action_code = int(match.group(1))
                    status = str(self.actions_status[action_code].value)
                    if str(event.value) != str(event.old_value):
                        action_status_mqtt_topic = action_status_topic
                        self.mqtt.publish(topic=action_status_mqtt_topic, payload=str(event.value), qos=2, retain=True)


                else:
                    print("Can't find action code")

            def tap_to_run_execute_actions(self, event: ValueUpdateEvent):
                print("********* Tap To Run Command ***********")
                for action in self.actions:
                    action_code = action["code"]
                    self.actions_status[action_code].post_value(ActionStatus.PENDING)
                self.execute_actions()

            def execute_actions(self):
                if str(self.linkage_rule_execution_status.value) != str(LinkageRuleExecutionStatus.DISABLE):
                    # Execute all actions defined in the rule
                    for action in self.actions:
                        try:
                            # self.perform_action(action)
                            executor_property = action['executor_property']
                            action_code = action["code"]
                            action_status_topic = self.linkage_rule_base_topic + f"/actions/actions-status/{action_code}"
                            # if self.actions_status[action_code].value != ActionStatus.COMPLETED:
                            # Example: Send an instruction to a device
                            if action['action_executor'] == "device_issue":
                                # print(self.actions_status[action_code].value)
                                if str(self.actions_status[action_code].value) == str(ActionStatus.PENDING):
                                    controller_uuid = action["controller_uuid"]
                                    device_uuid = action["device_uuid"]
                                    function_code = executor_property['function_code']
                                    function_value = executor_property['function_value']

                                    print(f"Executing action on {device_uuid}: {function_code} -> {function_value}")

                                    topic = f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{function_code}/set"
                                    MqttItem.get_create_item(name=topic).publish(payload=str(function_value), qos=2, retain=False)
                                    self.actions_status[action_code].post_value(ActionStatus.COMPLETED)
                                    print(self.actions_status[action_code].value)

                                    print(f"Publish on {topic} -> {function_value}")

                            elif action['action_executor'] == "delay":
                                if str(self.actions_status[action_code].value) == str(ActionStatus.PENDING):
                                    delay_seconds = int(executor_property['delay_seconds'])

                                    local_timezone = pytz.timezone('Asia/Tehran')
                                    present_datetime = datetime.now(tz=local_timezone)
                                    # Localize the datetime object to the specified time zone
                                    # local_datetime_with_tz = local_timezone.localize(present_datetime)
                                    print(present_datetime)
                                    desire_datetime = present_datetime + timedelta(seconds=delay_seconds)
                                    desire_time = desire_datetime.time()
                                    self.run.at(time=desire_time,
                                                callback=self.perform_timer_action, action_code=action_code)
                                    print(f"Action code:: {action_code} :: executing timer action :: next action execute for -> {delay_seconds}")
                                    self.actions_status[action_code].post_value(ActionStatus.IN_PROGRESS)
                                    return

                        except Exception as e:
                            print(f"Error in action execution process loop. Error description:: {e}")

                    number_of_actions_status = len(self.actions_status)
                    completed_action_counter = 0
                    for key in self.actions_status.keys():
                        print(f"action_code:: {key} :: action status:: {self.actions_status[key].value}")
                        if str(self.actions_status[key].value) == str(ActionStatus.COMPLETED):
                            completed_action_counter += 1

                    if completed_action_counter == number_of_actions_status:
                        self.linkage_rule_execution_status.post_value(LinkageRuleExecutionStatus.COMPLETED)
                        print("********** Complete linkage rule **************")
                        local_timezone = pytz.timezone('Asia/Tehran')
                        present_datetime = datetime.now(tz=local_timezone)
                        desire_datetime = present_datetime + timedelta(seconds=5)
                        desire_time = desire_datetime.time()
                        self.run.at(desire_time, self.set_actions_status_to_pending)
                        # for action_code, action_status in self.actions_status.items():
                        #     print(f"action_code:: {action_code} :: action status:: {action_status.value}")
                        #     self.actions_status[action_code].post_value(ActionStatus.PENDING)

            def perform_timer_action(self, action_code):
                if str(self.actions_status[action_code].value) == str(ActionStatus.IN_PROGRESS):
                    self.actions_status[action_code].post_value(ActionStatus.COMPLETED)
                    self.execute_actions()
                    return True
                else:
                    return False

            def set_actions_status_to_pending(self):
                if str(self.linkage_rule_execution_status.value) not in [str(LinkageRuleExecutionStatus.DISABLE), str(LinkageRuleExecutionStatus.IN_PROGRESS)]:
                    for action_code, action_status in self.actions_status.items():
                        if str(self.actions_status[action_code].value) != str(ActionStatus.IN_PROGRESS):
                            self.actions_status[action_code].post_value(ActionStatus.PENDING)
                        print(f"action_code:: {action_code} :: action status:: {action_status.value}")

            # def perform_action(self, action):


        # config_file_name = 'a'
        #
        # path = os.path.join(Path(os.getcwd()), Path(f"rule_config/{config_file_name}.json"))
        # with open(path, 'r', encoding='utf-8') as file_handler:
        #     config = json.load(file_handler)
        #     LinkageRule(config)


        config = {{ config }}

        LinkageRule(config)
        ''')
        config_str = json.dumps(self.rule_config)
        # Render the template with dynamic values
        self.rule_code = template.render(config=config_str)

    def set_rule_topics_authorization(self):
        # get old rule, delete all related authorization rules from mqtt broker and setup new ones
        # set authorization rule for home users
        self.delete_linkage_rule_topics_authorization()
        base_url = os.environ.get('emqx_base_url')
        emqx_api_username = os.environ.get('emqx_api_username')
        emqx_api_password = os.environ.get('emqx_api_password')
        base_linkage_rule_topics_address = f"v1/projects/{self.project.uuid}/homes/{self.home.uuid}/linkage-rules/{self.rule_instance.uuid}"

        home_users = HomeUser.objects.filter(parent_project=self.project, parent_home=self.home).all()
        for home_user in home_users:
            get_client_rules_endpoint = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{home_user.mqtt_client_id}"

            auth_header = "Basic " + base64.b64encode(
                (str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
            header = {'Content-Type': 'application/json',
                      'Authorization': auth_header
                      }
            try:
                response = requests.get(get_client_rules_endpoint, headers=header)
                if response.status_code == 200:
                    print(
                        f"successfully get client authorization rules from broker. now we need to add all linkage rules to it and PUT it again.")
                    all_client_rules = json.loads(response.content.decode("utf-8"))
                    rules_field: list = all_client_rules["rules"]

                    tap_to_run_trigger_rule = {
                                "action": "publish",
                                "topic": base_linkage_rule_topics_address + "/actions/trigger/",
                                "permission": "allow",
                                "retain": "false"
                            }
                    set_linkage_rule_status = {
                        "action": "publish",
                        "topic": base_linkage_rule_topics_address + "/status/set",
                        "permission": "allow",
                        "retain": "false"
                    }
                    get_linkage_rule_status = {
                        "action": "subscribe",
                        "topic": base_linkage_rule_topics_address + "/status/get",
                        "permission": "allow",
                    }
                    linkage_rule_actions_status = {
                        "action": "subscribe",
                        "topic": base_linkage_rule_topics_address + "/actions/actions-status/+",
                        "permission": "allow",
                    }
                    must_added_rules = [tap_to_run_trigger_rule, set_linkage_rule_status, get_linkage_rule_status, linkage_rule_actions_status]
                    # because '#' was contained in the end of rules_field, so we add 'must_added_rules' to the start of
                    # rules_field list.
                    rules_field = must_added_rules + rules_field

                    put_client_rule_endpoint = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{home_user.mqtt_client_id}"
                    response = requests.put(put_client_rule_endpoint, data=json.dumps(all_client_rules).encode('utf-8'),
                                            headers=header)
                    if response.status_code == 204:
                        print(f"Successfully added client linkage rules to client. linkage rule id:: {self.rule_instance.uuid} client id:: {home_user.mqtt_client_id}.")
                        return True
                else:
                    print(
                        f"get error while putting linkage rule for client. client id:: {home_user.mqtt_client_id} ::  error:: {response.content.decode()}")
                    return False
            except Exception as e:
                print(f"mqtt client set linkage rule was unsuccessfully. Reason:: {e}")
                return False

    def delete_linkage_rule_topics_authorization(self):
        base_url = os.environ.get('emqx_base_url')
        emqx_api_username = os.environ.get('emqx_api_username')
        emqx_api_password = os.environ.get('emqx_api_password')
        base_linkage_rule_topics_address = f"v1/projects/{self.project.uuid}/homes/{self.home.uuid}/linkage-rules/{self.rule_instance.uuid}"
        regex_pattern = r"v1/projects/[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}/homes/[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}/linkage-rules/[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}/"

        home_users = HomeUser.objects.filter(parent_project=self.project, parent_home=self.home).all()
        for home_user in home_users:
            get_client_rules_endpoint = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{home_user.mqtt_client_id}"

            auth_header = "Basic " + base64.b64encode(
                (str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
            header = {'Content-Type': 'application/json',
                      'Authorization': auth_header
                      }
            try:
                response = requests.get(get_client_rules_endpoint, headers=header)
                if response.status_code == 200:
                    print(f"successfully get client authorization rules from broker. now we need to delete all linkage rules from it and PUT it again.")
                    all_client_rules = json.loads(response.content.decode("utf-8"))
                    rules_field: list = all_client_rules["rules"]
                    for index, rule in enumerate(rules_field):
                        rule_topic = rule["topic"]
                        match = re.search(regex_pattern, rule_topic)
                        if match:
                            rules_field.pop(index)
                    # rules_field is point to rules filed of all_client_rules, so each changes on it, seen on
                    # all_client_rules. So we have cleaned all_client_rules now.
                    put_client_rule_endpoint = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{home_user.mqtt_client_id}"
                    response = requests.put(put_client_rule_endpoint, data=json.dumps(all_client_rules).encode('utf-8'), headers=header)
                    if response.status_code == 204:
                        print(f"Successfully remove client linkage rules. client id:: {home_user.mqtt_client_id}.")
                        return True
                else:
                    print(
                        "get error while deleting user from password_based:built_in_database authentication engine. error:: " + response.content.decode())
                    return False
            except Exception as e:
                print(f"mqtt user deletion was unsuccessfully. Reason:: {e}")
                return False

    def place_linkage_rule_file_to_rule_engine_rules_folder(self):
        try:
            with open(file=os.path.join(Path(BASE_DIR.parent),
                                        Path(f'RuleEngineService/rules/rule_{self.rule_instance.uuid}')), mode='x',
                      encoding='utf-8') as file_handler:
                # file is not exist and we create new one
                if self.rule_code:
                    file_handler.write(self.rule_code)
                else:
                    print(f"Can't create linkage rule file, because of lack of generated rule code. rule id :: {self.rule_instance.uuid}")
        except FileExistsError as e:
            print(f"file is exist and we need to rewrite it.")
            with open(file=os.path.join(Path(BASE_DIR.parent),
                                        Path(f'RuleEngineService/rules/rule_{self.rule_instance.uuid}')), mode='w',
                      encoding='utf-8') as file_handler:
                if self.rule_code:
                    file_handler.write(self.rule_code)
                else:
                    print(f"Can't create linkage rule file, because of lack of generated rule code. rule id :: {self.rule_instance.uuid}")