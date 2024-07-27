from django.db import models


class Device(models.Model):
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class FourPoleSwitch(Device):
    # Additional fields specific to FourPoleSwitch can be added here
    pass


class SwitchSetting(models.Model):
    switch = models.ForeignKey(FourPoleSwitch, related_name='settings', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}: {self.value}"


class SwitchState(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='switch_states')
    pole_1 = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class DataPoint(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='switch_dataPoints')
    datapoint_name = models.CharField(max_length=100)
    datapoint_value = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)



# device = Device(name='device1', device_type='1')
#
# SwitchState(device=device, pole_1=True)
#
# print(SwitchState)