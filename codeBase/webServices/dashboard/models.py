import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_advance_thumbnail import AdvanceThumbnailField

from .utils import generate_random_password, generate_random_username, generate_random_id


def generate_rand_id_for_controller():
    return ''.join(["controller_", generate_random_id()])


def generate_rand_id_for_client():
    return ''.join(["client_", generate_random_id()])



class DashboardUser(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboardUser', related_query_name='dashboardUser')
    avatar = models.ImageField(upload_to="dashboard_users_avatar/original_files/", blank=True, null=True)
    avatar_thumbnail = AdvanceThumbnailField(source_field='avatar', upload_to='dashboard_users_avatar/thumbnail_files/',
                                             null=True, blank=True, size=(300, 300))

    telegramID = models.CharField(max_length=100, default='', blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='dashboardUser', related_query_name='dashboardUser')



class CityCoordinates(models.Model):
    city_name = models.CharField(max_length=100, blank=False, null=False)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.city_name}"


class Project(models.Model):
    class ProjectStatusChoices(models.TextChoices):
        DISABLE = 'disable', 'disable'
        ENABLE = 'enable', 'enable'
        IN_CONSTRUCTION = 'in_construction', 'construction'
        MAINTENANCE = 'maintenance', 'maintenance'

    project_name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    owner_phone_number = models.CharField(max_length=100, blank=True, null=True)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    # used for web app/tablet. set default icon to artiman company icon.
    # project_icon = models.ImageField(upload_to="project_icons/")
    city = models.ForeignKey(CityCoordinates, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    project_lock = models.BooleanField(blank=False, null=False, default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_created_by")
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_edited_by")
    last_modified = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.CASCADE))
    status = models.CharField(max_length=50, choices=ProjectStatusChoices.choices, default=ProjectStatusChoices.DISABLE)

    # class Meta:
    #     permissions = [('add_project', 'Can add project'),
    #                    ('change_project', 'Can change project'),
    #                    ('delete_project', 'Can delete project'),
    #                    ('view_project', 'Can view project'),
    #                    ('change_project_lock', 'Can change project lock status')
    #                    ]


class Home(models.Model):
    home_name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    owner_phone_number = models.CharField(max_length=100, blank=True, null=True)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="homes")
    building = models.CharField(max_length=100, blank=True, null=True)
    floor = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=100, blank=True, null=True)

    # has_webapp = models.BooleanField(blank=False, null=False, default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='home_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='home_edited_by')
    last_modified = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.CASCADE))


class HomeUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='homeUser', related_query_name='homeUser')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="homeUsers")
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.CASCADE))
    desc = models.CharField(max_length=500, blank=True)
    is_tablet_user = models.BooleanField(blank=False, null=False, default=False)
    is_web_app_user = models.BooleanField(blank=False, null=False, default=False)
    avatar = models.ImageField(upload_to="users_avatar/original_files/", blank=True, null=True)
    avatar_thumbnail = AdvanceThumbnailField(source_field='avatar', upload_to='users_avatar/thumbnail_files/',
                                             null=True, blank=True, size=(300, 300))

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='homeUser_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='homeUser_edited_by')
    last_modified = models.DateTimeField(auto_now=True)

    mqtt_client_id = models.CharField(max_length=100, blank=False, null=False, default=generate_rand_id_for_client)
    mqtt_username = models.CharField(max_length=100, blank=False, null=False, default=generate_random_username)
    mqtt_password = models.CharField(max_length=100, blank=False, null=False, default=generate_random_password)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         HomeUser.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if hasattr(instance, 'homeUser'):
#         instance.homeUser.save()
#     else:
#         HomeUser.objects.create(user=instance)


class Tablet(models.Model):
    status = models.BooleanField(blank=False, null=False, default=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="tablets")
    # if broker enabled in tablet, we need to ip address and port number of it to config controllers
    tablet_has_internal_mqtt_broker = models.BooleanField(blank=False, null=False, default=False)
    tablet_ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, default='192.168.1.10')
    tablet_internal_mqtt_broker_port = models.IntegerField(blank=False, null=False, default=1883)
    tablet_internal_mqtt_broker_username = models.CharField(max_length=100, blank=True, null=True,
                                                            default=generate_random_username)
    tablet_internal_mqtt_broker_password = models.CharField(max_length=100, blank=True, null=True,
                                                            default=generate_random_password)


class Controller(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)

    class ControllerStatusChoices(models.TextChoices):
        DISABLE = 'disable', 'disable'
        ENABLE = 'enable', 'enable'
        ERROR = 'error', 'error'

    class UartBaudRateChoices(models.TextChoices):
        BAUD_75 = '75', '75'
        BAUD_300 = '300', '300'
        BAUD_1200 = '1200', '1200'
        BAUD_2400 = '2400', '2400'
        BAUD_4800 = '4800', '4800'
        BAUD_9600 = '9600', '9600'
        BAUD_14400 = '14400', '14400'
        BAUD_19200 = '19200', '19200'
        BAUD_28800 = '28800', '28800'
        BAUD_38400 = '38400', '38400'
        BAUD_57600 = '57600', '57600'
        BAUD_115200 = '115200', '115200'
    
    class DataBitsChoices(models.TextChoices):
        DATA_BIT_5 = "5", "5"
        DATA_BIT_6 = "6", "6"
        DATA_BIT_7 = "7", "7"
        DATA_BIT_8 = "8", "8"
    
    class ParityChoices(models.TextChoices):
        NONE = "None", "None"
        ODD = "Odd", "Odd"
        EVEN = "Even", "Even"

    class StopBitsChoices(models.TextChoices):
        STOP_BIT_1 = "1", "1"
        STOP_BIT_2 = "2", "2"

    class FlowControlChoices(models.TextChoices):
        NONE = "None", "None"
        RTS_CTS = "RTS/CTS", "RTS/CTS"
        XON_XOFF = "Xon/Xoff", "Xon/Xoff"

    status = models.CharField(max_length=50, choices=ControllerStatusChoices.choices, default=ControllerStatusChoices.DISABLE)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="controllers")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='controller_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='controller_edited_by')
    last_modified = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.CASCADE))

    # general properties
    enable_internal_server = models.BooleanField(blank=False, null=False, default=False)

    ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, default='192.168.1.3')
    port_number = models.IntegerField(blank=True, null=True)
    # internal properties
    uart_baud_rate = models.CharField(max_length=50, blank=False, null=False, choices=UartBaudRateChoices.choices, default=UartBaudRateChoices.BAUD_9600)
    uart_data_bits = models.CharField(max_length=50, blank=False, null=False, choices=DataBitsChoices.choices, default=DataBitsChoices.DATA_BIT_7)
    uart_parity = models.CharField(max_length=50, blank=False, null=False, choices=ParityChoices.choices, default=ParityChoices.NONE)
    uart_stop_bits = models.CharField(max_length=50, blank=False, null=False, choices=StopBitsChoices.choices, default=StopBitsChoices.STOP_BIT_1)
    uart_flow_control = models.CharField(max_length=50, blank=False, null=False, choices=FlowControlChoices.choices, default=FlowControlChoices.NONE)

    # mqtt properties
    # credential
    mqtt_client_id = models.CharField(max_length=100, blank=False, null=False,
                                      default=generate_rand_id_for_controller)
    mqtt_username = models.CharField(max_length=100, blank=False, null=False,
                                     default=generate_random_username)
    mqtt_password = models.CharField(max_length=100, blank=False, null=False,
                                     default=generate_random_password)

    # mtls files path(or save cert in database)/it's better to only create certs
    # when we want to get controller config file
    client_key_pem = models.TextField(max_length=10000, blank=True, null=True)
    client_cert_pem = models.TextField(max_length=10000, blank=True, null=True)

    def __str__(self):
        return self.name


class Zone(models.Model):
    zone_name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    description = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="home_zones")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zone_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zone_edited_by')
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.zone_name


class DeviceBase(models.Model):
    # name that shows in all devices list
    name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="home_devices")
    parent_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="zone_devices")
    parent_controller = models.ForeignKey(Controller, on_delete=models.CASCADE, related_name="controller_devices")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_edited_by')
    last_modified = models.DateTimeField(auto_now=True)

    modbus_id = models.IntegerField(blank=True, null=True)
    modbus_channel = models.IntegerField(blank=True, null=True)
    # device_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('device_type', 'object_id')

    def __str__(self):
        return self.name


class BooleanValues(models.TextChoices):
    TRUE = 'true', 'true'
    FALSE = 'false', 'false'


class ValueTypes(models.TextChoices):
    # Actual value ↓      # ↓ Displayed on front-end
    BOOLEAN = 'BOOLEAN', 'boolean'
    INTEGER = 'INTEGER', 'integer'
    DECIMAL = 'DECIMAL', 'decimal'
    FLOAT = 'FLOAT', 'float'
    STRING = 'STRING', 'string'
    JSON = 'JSON', 'json'
    DATE = 'DATE', 'date'
    DATETIME = 'DATETIME', 'dateTime'


class FunctionTypes(models.TextChoices):
    SWITCH = 'switch', 'switch'
    THERMOSTAT = 'thermostat', 'thermostat'

class FunctionIOPermissionChoices(models.TextChoices):
    READ_ONLY = "R", "Read Only"
    WRITE_ONLY = "W", "Write Only"
    READ_WRITE = "R/W", "Read/Write" 

class ModbusDataModelChoices(models.TextChoices):
    DISCRETE_INPUT = "discrete_input", "Discrete input"
    COIL = "coil", "coil"
    INPUT_REGISTER = "input_register", "Input register"
    HOLDING_REGISTER = "holding_register", "Holding register"

class InternalBufferDataModelChoices(models.TextChoices):
    BIT_1 = "1b", "1 Bit"
    BIT_4 = "4b", "4 bit"
    BIT_8 = "8b", "8 bit"
    BIT_16 = "16b", "16 bit"
    BIT_32 = "32b", "32 bit"
    BIT_64 = "64b", "64 bit"

class DataPointFunction(models.Model):
    device_base = models.ForeignKey(DeviceBase, on_delete=models.CASCADE, related_name='functions')
    display_name = models.CharField(max_length=255, blank=False, null=False)   # e.g., "set_point_temperature" or "temp_value"
    function_name = models.CharField(max_length=255, blank=False, null=False)  # e.g., "spt" or "temp"
    value = models.CharField(max_length=255, default='null')
    value_type = models.CharField(max_length=255, choices=ValueTypes.choices, default=ValueTypes.STRING)
    io_permission = models.CharField(max_length=20, choices=FunctionIOPermissionChoices.choices, default=FunctionIOPermissionChoices.READ_WRITE)
    
    modbus_read_data_model = models.CharField(max_length=30, choices=ModbusDataModelChoices.choices, default=ModbusDataModelChoices.INPUT_REGISTER)
    modbus_read_start_address = models.IntegerField(blank=True, null=True)
    modbus_read_quantity = models.IntegerField(blank=True, null=True)
    modbus_write_data_model = models.CharField(max_length=30, choices=ModbusDataModelChoices.choices, default=ModbusDataModelChoices.HOLDING_REGISTER)
    modbus_write_start_address = models.IntegerField(blank=True, null=True)
    modbus_write_quantity = models.IntegerField(blank=True, null=True)

    internal_buffer_read_data_model = models.CharField(max_length=30, choices=InternalBufferDataModelChoices.choices, default=InternalBufferDataModelChoices.BIT_1)
    internal_buffer_read_start_address = models.IntegerField(blank=True, null=True)
    internal_buffer_read_quantity = models.IntegerField(blank=True, null=True)
    internal_buffer_write_data_model = models.CharField(max_length=30, choices=InternalBufferDataModelChoices.choices, default=InternalBufferDataModelChoices.BIT_1)
    internal_buffer_write_start_address = models.IntegerField(blank=True, null=True)
    internal_buffer_write_quantity = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return f"{self.device_base.name} - {self.function_name}"


# FourPoleSwitch with 4 switches
class SwitchDataPointFunction(DataPointFunction):
    function_type = models.CharField(max_length=255, default=FunctionTypes.SWITCH)
    switch_id = models.IntegerField()

    def __str__(self):
        return f"{self.device_base.name} - Switch {self.switch_id}"


class ThermostatDataPointFunction(DataPointFunction):
    function_type = models.CharField(max_length=255, default=FunctionTypes.THERMOSTAT)
    # set as datapoint
    # temp_min = models.CharField(max_length=255, default=12)
    # temp_max = models.CharField(max_length=255, default=30)

    def __str__(self):
        return f"{self.device_base.name} - {self.display_name}"

# # this is the standard way to create distict class for dataPoint functions modbus properties, because it is possible some datapoint in some devices have not 
# # correspond modbus properties
# class ModbusDataModelChoices(models.TextChoices):
#     DISCRETE_INPUT = "discrete_input", "Discrete input"
#     COIL = "coil", "coil"
#     INPUT_REGISTER = "input_register", "Input register"
#     HOLDING_REGISTER = "holding_register", "Holding register"

# class DataPointFunctionModbusProperties(models.Model):
#     data_point_function_base = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="modbus_properties")
#     modbus_data_model_type = models.CharField(max_length=30, choices=ModbusDataModelChoices.choices, default=ModbusDataModelChoices.INPUT_REGISTER)
#     start_address = models.IntegerField(blank=True, null=True)
#     quantity = models.IntegerField(blank=True, null=True)



class Switch(DeviceBase):
    pass


class FourPoleSwitch(Switch):

    def __str__(self):
        return f"{self.name} - 4 Pole Switch"


class FivePoleSwitch(Switch):
    def __str__(self):
        return f"{self.name} - 5 Pole Switch"


class Thermostat(DeviceBase):
    # set_point_temperature = models.FloatField()
    # current_temperature = models.FloatField()
    def __str__(self):
        return f"{self.name} - Thermostat"


class FourPoleThermostat(DeviceBase):
    # set_point_temperature = models.FloatField()
    # current_temperature = models.FloatField()
    def __str__(self):
        return f"{self.name} - Thermostat"


class TenPoleThermostat(DeviceBase):
    # set_point_temperature = models.FloatField()
    # current_temperature = models.FloatField()
    def __str__(self):
        return f"{self.name} - Thermostat"
    
class ControllerDevice(DeviceBase):
    # set_point_temperature = models.FloatField()
    # current_temperature = models.FloatField()
    def __str__(self):
        return f"{self.name} - controller device"


class DeviceProxy(models.Model):
    device_base = models.ForeignKey(DeviceBase, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.device_base.name} ({self.content_type})"


class DeviceSwitchActions(models.Model):
    class SwitchStatus(models.TextChoices):
        ON = 'on', 'on'
        OFF = 'off', 'off'
        TOGGLE = 'toggle', 'toggle'

    ref_data_point = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="ref_data_point")
    ref_data_point_status = models.CharField(max_length=50, blank=False, null=False, choices=SwitchStatus.choices, default=SwitchStatus.ON)
    target_data_point = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="target_data_point")
    target_data_point_status = models.CharField(max_length=255, blank=False, null=False)
    target_data_point_status_type = models.CharField(max_length=255, choices=ValueTypes.choices, default=ValueTypes.STRING)


####################### UI Section #########################

class UIElementBackgroundImage(models.Model):
    background_image = models.ImageField(upload_to="ui_elements_background_images/", blank=True, null=True)
    background_image_thumbnail = AdvanceThumbnailField(source_field='background_image', upload_to='ui_elements_background_images/thumbnail_files/',
                                                       null=True, blank=True, size=(200, 200))
    style_options = models.CharField(max_length=1000, blank=True, null=True)



class UIBase(models.Model):

    class ButtonTypes(models.TextChoices):
        SWITCH = 'switch', 'Switch button'
        PUSH_BUTTON = 'push_button', 'Push button'
        THERMOSTAT = 'thermostat', 'Thermostat button'
        CURTAIN = 'curtain', 'Curtain button'

    # the names that show in all ui elements list
    name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="home_ui_elements")
    parent_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="zone_ui_elements")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ui_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ui_edited_by')
    last_modified = models.DateTimeField(auto_now=True)

    button_name = models.CharField(max_length=100, blank=False, null=False)
    on_text = models.CharField(max_length=100, blank=False, null=False)
    off_text = models.CharField(max_length=100, blank=False, null=False)
    on_color = models.CharField(max_length=100, blank=False, null=False)
    off_color = models.CharField(max_length=100, blank=False, null=False)
    # fontawesome <i> code
    on_icon = models.CharField(max_length=255, blank=False, null=False)
    off_icon = models.CharField(max_length=255, blank=False, null=False)
    add_to_home = models.BooleanField(blank=False, null=False, default=False)
    tablet_mode_background_image = models.ForeignKey(UIElementBackgroundImage, on_delete=models.CASCADE)



class SwitchUI(UIBase):
    button_type = models.CharField(max_length=50, blank=False, null=False, choices=UIBase.ButtonTypes.choices, default=UIBase.ButtonTypes.SWITCH)
    data_point_function = models.ForeignKey(SwitchDataPointFunction, on_delete=models.CASCADE, related_name="switch_button_data_point")


class PushButtonUI(UIBase):
    button_type = models.CharField(max_length=50, blank=False, null=False, choices=UIBase.ButtonTypes.choices, default=UIBase.ButtonTypes.PUSH_BUTTON)
    data_point_function = models.ForeignKey(SwitchDataPointFunction, on_delete=models.CASCADE, related_name="push_button_data_point")


class CurtainUI(UIBase):
    button_type = models.CharField(max_length=50, blank=False, null=False, choices=UIBase.ButtonTypes.choices, default=UIBase.ButtonTypes.CURTAIN)
    open_data_point_function = models.ForeignKey(SwitchDataPointFunction, on_delete=models.CASCADE, related_name="open_data_point")
    close_data_point_function = models.ForeignKey(SwitchDataPointFunction, on_delete=models.CASCADE, related_name="close_data_point")
    animation_duration = models.IntegerField(blank=False, null=False, default=5000)


class ThermostatUI(UIBase):
    button_type = models.CharField(max_length=50, blank=False, null=False, choices=UIBase.ButtonTypes.choices, default=UIBase.ButtonTypes.THERMOSTAT)
    power_status_function = models.ForeignKey(ThermostatDataPointFunction, on_delete=models.CASCADE, related_name="power_status")
    current_temp_function = models.ForeignKey(ThermostatDataPointFunction, on_delete=models.CASCADE, related_name="current_temp")
    target_temp_function = models.ForeignKey(ThermostatDataPointFunction, on_delete=models.CASCADE, related_name="target_temp")
    speed_function = models.ForeignKey(ThermostatDataPointFunction, on_delete=models.CASCADE, related_name="speed")
    control_mode_function = models.ForeignKey(ThermostatDataPointFunction, on_delete=models.CASCADE, related_name="control_mode")    # auto/manual
    operation_mode_function = models.ForeignKey(ThermostatDataPointFunction, on_delete=models.CASCADE, related_name="operation_mode")  # heat/cool


class UIProxy(models.Model):
    ui_base = models.ForeignKey(UIBase, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.ui_base.name} ({self.content_type})"




# class FourPoleSwitch(models.Model):
#     name = models.CharField(max_length=100)
#     home = models.ForeignKey(Home, related_name='four_pole_switches', on_delete=models.CASCADE)
#     # Additional fields specific to FourPoleSwitch
#
#     def __str__(self):
#         return self.name
#
#
# class Thermostat(models.Model):
#     name = models.CharField(max_length=100)
#     home = models.ForeignKey(Home, related_name='thermostats', on_delete=models.CASCADE)
#     temperature = models.DecimalField(max_digits=5, decimal_places=2)
#     # Additional fields specific to Thermostat
#
#     def __str__(self):
#         return self.name
#
#
# class DataPoint(models.Model):
#     device = models.ForeignKey(Device, related_name='datapoints', on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     value = models.CharField(max_length=100)
#
#     def __str__(self):
#         return f"{self.name}: {self.value}"


# class mqtt_client_properties():
#     reconnect_rate
#     reconnect_time
#     broker_address
#     client_id
#     password
#     username
#     ...


# class scenes():
#     added_to_home
#     zone_to_added
