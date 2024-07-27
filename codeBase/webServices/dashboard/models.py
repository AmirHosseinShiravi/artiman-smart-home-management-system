import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import generate_random_password, generate_random_username, generate_random_id


# Create your models here.


class CityCoordinates(models.Model):
    city_name = models.CharField(max_length=100, blank=False, null=False)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)


class Project(models.Model):
    project_name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    owner_phone_number = models.CharField(max_length=100, blank=True, null=True)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    # used for web app/tablet. set default icon to artiman company icon.
    project_icon = models.ImageField(upload_to="project_icons/")
    city = models.ForeignKey(CityCoordinates, on_delete=models.PROTECT)
    address = models.CharField(max_length=255, blank=True, null=True)
    project_lock = models.BooleanField(blank=False, null=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="project_created_by")
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="project_edited_by")
    last_modified = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.PROTECT)


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
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='home_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='home_edited_by')
    last_modified = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.PROTECT)


class HomeUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="homeUsers")
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    desc = models.TextField(max_length=500, blank=True)
    is_tablet_user = models.BooleanField(blank=False, null=False)
    is_web_app_user = models.BooleanField(blank=False, null=False)
    avatar = models.ImageField(upload_to="users_avatar/original_files/", blank=True, null=True)
    # avatar_thumbnail = AdvanceThumbnailField(source_field='avatar', upload_to='users_avatar/thumbnail_files/',
    #                                          null=True, blank=True, size=(300, 300))


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        HomeUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Tablet(models.Model):
    status = models.BooleanField(blank=False, null=False, default=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="tablets")
    # if broker enabled in tablet, we need to ip address and port number of it to config controllers
    tablet_has_internal_mqtt_broker = models.BooleanField(blank=False, null=False, default=False)
    tablet_ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=False)
    tablet_internal_mqtt_broker_port = models.IntegerField(blank=False, null=False, default=1883)
    tablet_internal_mqtt_broker_username = models.CharField(max_length=100, blank=True, null=True,
                                                            default=generate_random_username(length=8))
    tablet_internal_mqtt_broker_password = models.CharField(max_length=100, blank=True, null=True,
                                                            default=generate_random_password(length=12))


class Controller(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="controllers")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='controller_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='controller_edited_by')
    last_modified = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.PROTECT)

    # general properties
    ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=False)
    port_number = models.IntegerField(blank=False, null=False)
    # internal properties
    uart_baud_rate = models.IntegerField(blank=False, null=False)

    # mqtt properties
    # credential
    mqtt_client_id = models.CharField(max_length=100, blank=False, null=False,
                                      default="controller_" + generate_random_id(length=10))
    mqtt_username = models.CharField(max_length=100, blank=False, null=False,
                                     default=generate_random_username(length=10))
    mqtt_password = models.CharField(max_length=100, blank=False, null=False,
                                     default=generate_random_password(length=20))

    # mtls files path(or save cert in database)/it's better to only create certs when we want to get controller config file
    client_key_pem = models.CharField(max_length=10000, blank=False, null=False)
    client_cert_pem = models.CharField(max_length=10000, blank=False, null=False)


# class ControllerProperties(models.Model):
#     controller = models.OneToOneField(Controller, on_delete=models.CASCADE)
#     # general properties
#     ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=False)
#     port_number = models.IntegerField(blank=False, null=False)
#     # internal properties
#     uart_baud_rate = models.IntegerField(blank=False, null=False)
#
#     # mqtt properties
#     # credential
#     mqtt_client_id = models.CharField(max_length=100, blank=False, null=False, default="controller_" + generate_random_id(length=10))
#     mqtt_username = models.CharField(max_length=100, blank=False, null=False, default=generate_random_username(length=10))
#     mqtt_password = models.CharField(max_length=100, blank=False, null=False, default=generate_random_password(length=20))
#
#     # mtls files path(or save cert in database)/it's better to only create certs when we want to get controller config file
#     client_key_pem = models.CharField(max_length=10000, blank=False, null=False)
#     client_cert_pem = models.CharField(max_length=10000, blank=False, null=False)


class Zone(models.Model):
    pass


class DeviceBase(models.Model):
    # name that shows in all devices list
    name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="home_devices")
    parent_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="zone_devices")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='device_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='device_edited_by')
    last_modified = models.DateTimeField(auto_now=True)

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


class DataPointFunction(models.Model):
    device_base = models.ForeignKey(DeviceBase, on_delete=models.CASCADE, related_name='functions')
    display_name = models.CharField(max_length=255, blank=False, null=False)   # e.g., "set_point_temperature" or "temp_value"
    function_name = models.CharField(max_length=255, blank=False, null=False)  # e.g., "spt" or "temp"
    value = models.CharField(max_length=255, default='null')
    value_type = models.CharField(max_length=255, choices=ValueTypes.choices, default=ValueTypes.STRING)

    def __str__(self):
        return f"{self.device_base.name} - {self.function_name}: {self.value}"


# FourPoleSwitch with 4 switches
class SwitchDataPointFunction(DataPointFunction):
    function_type = models.CharField(max_length=255, default=FunctionTypes.SWITCH)
    switch_id = models.IntegerField()

    def __str__(self):
        return f"{self.device_base.name} - Switch {self.switch_id}: {self.value}"


class ThermostatDataPointFunction(DataPointFunction):
    function_type = models.CharField(max_length=255, default=FunctionTypes.THERMOSTAT)
    # set as datapoint
    # temp_min = models.CharField(max_length=255, default=12)
    # temp_max = models.CharField(max_length=255, default=30)

    def __str__(self):
        return f"{self.device_base.name} - {self.function_name}: {self.value}"


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
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ui_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ui_edited_by')
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


class SwitchUI(UIBase):
    button_type = models.CharField(max_length=50, blank=False, null=False, choices=UIBase.ButtonTypes.choices, default=UIBase.ButtonTypes.SWITCH)
    data_point_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="switch_button_data_point")


class PushButtonUI(UIBase):
    button_type = models.CharField(max_length=50, blank=False, null=False, choices=UIBase.ButtonTypes.choices, default=UIBase.ButtonTypes.PUSH_BUTTON)
    data_point_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="push_button_data_point")


class CurtainUI(UIBase):
    button_type = models.CharField(max_length=50, blank=False, null=False, choices=UIBase.ButtonTypes.choices, default=UIBase.ButtonTypes.CURTAIN)
    open_data_point_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="open_data_point")
    close_data_point_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="close_data_point")


class ThermostatUI(UIBase):
    button_type = models.CharField(max_length=50, blank=False, null=False, choices=UIBase.ButtonTypes.choices, default=UIBase.ButtonTypes.THERMOSTAT)
    current_temp_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="current_temp")
    target_temp_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="target_temp")
    speed_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="speed")
    control_mode_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="control_mode")    # auto/manual
    operation_mode_function = models.ForeignKey(DataPointFunction, on_delete=models.CASCADE, related_name="operation_mode")  # heat/cool


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
