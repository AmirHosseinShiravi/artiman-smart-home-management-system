import uuid as uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.


class DeviceBase(models.Model):
    # name that shows in all devices list
    name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    # descriptions = models.CharField(max_length=1000, blank=True, null=True)
    # created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='device_created_by')
    # created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    # last_edited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='device_edited_by')
    # last_modified = models.DateTimeField(auto_now=True)

    # device_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('device_type', 'object_id')

    class Meta:
        abstract = False

    def __str__(self):
        return self.name


class Function(models.Model):
    device_base = models.ForeignKey(DeviceBase, on_delete=models.CASCADE, related_name='functions')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    data_point_function = models.CharField(max_length=255)  # e.g., "setpoint_temperature" or "temp_value"

    def __str__(self):
        return f"{self.device_base.name} - {self.name}: {self.value}"


# FourPoleSwitch with 4 switches
class SwitchFunction(Function):
    switch_id = models.IntegerField()

    def __str__(self):
        return f"{self.device_base.name} - Switch {self.switch_id}: {self.value}"


class ThermostatFunction(Function):
    def __str__(self):
        return f"{self.device_base.name} - {self.data_point_function}: {self.value}"


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


class DeviceProxy(models.Model):
    device_base = models.ForeignKey(DeviceBase, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.device_base.name} ({self.content_type})"


class ValueTypes(models.TextChoices):
    # Actual value ↓      # ↓ Displayed on front-end
    BOOLEAN = 'BOOLEAN', 'boolean(true or false)'
    INTEGER = 'INTEGER', 'integer'
    DECIMAL = 'DECIMAL', 'decimal'
    FLOAT = 'FLOAT', 'float'
    STRING = 'STRING', 'string'
    JSON = 'JSON', 'json'
    DATE = 'DATE', 'date'
    DATETIME = 'DATETIME', 'dateTime'
