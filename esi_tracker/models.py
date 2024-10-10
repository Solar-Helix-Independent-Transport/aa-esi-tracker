"""
App Models
Create your models in here
"""

# Django
from django.db import models

from solo.models import SingletonModel

from .enums import ESIStatus

class ESITrackerConfiguration(SingletonModel):
    """Model for app configuration"""
    
    seconds_between_checks = models.IntegerField(default=600)

    class Meta:
        default_permissions = ()


class ESIEndpoint(models.Model):
    """ESI Status Snapshot"""
    endpoint = models.TextField(max_length=512)
    method = models.TextField(max_length=32)
    route = models.TextField(max_length=512)
    tag = models.TextField(max_length=512)

    class Meta:
        default_permissions = ()


class ESIEndpointStatus(models.Model):
    """ESI Status Snapshot"""
    date = models.DateTimeField()
    status = models.IntegerField(choices=ESIStatus.choices())
    endpoint = models.ForeignKey(ESIEndpoint, on_delete=models.CASCADE)

    class Meta:
        default_permissions = ()
