from django.db import models

# Create your models here.

class SystemRuntimeLog(models.Model):
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True,null=True)
    reason_code = models.PositiveIntegerField()