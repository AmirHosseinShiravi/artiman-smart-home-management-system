from django.db import models
import uuid
from dashboard.models import Project, Home, Zone
from django.contrib.auth.models import User
# Create your models here.


class LinkageRule(models.Model):

    class RuleStatus(models.TextChoices):
        ENABLE = 'enable', 'enable'
        DISABLE = 'disable', 'disable'

    name = models.CharField(max_length=100, blank=False, null=False)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, blank=False, null=False)
    status = models.CharField(max_length=50, choices=RuleStatus.choices, default=RuleStatus.ENABLE)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent_home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name="linkage_rules")
    # parent_zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="zone_linkage_rules")
    rule_config = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='linkage_rules_created_by')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='linkage_rules_edited_by')
    last_modified = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(blank=False, null=False)
    # deleted_by = models.ForeignKey(User, on_delete=models.PROTECT)
