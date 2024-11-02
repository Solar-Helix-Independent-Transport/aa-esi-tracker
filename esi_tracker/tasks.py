"""App Tasks"""

# Standard Library
import logging

# Third Party
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from requests import get

from .models import ESIEndpoint, ESIEndpointStatus
from .enums import ESIStatus
from .providers import DataProvider
logger = logging.getLogger(__name__)

@shared_task
def esi_status_snapshot():
    time = timezone.now()
    url = "https://esi.evetech.net/status.json?version=latest"
    
    esi_status = get(url).json()
    updates = []
    for ep in esi_status:
        _ep, _new = ESIEndpoint.objects.get_or_create(
            endpoint = ep["endpoint"],
            method = ep["method"],
            route = ep["route"],
            tag = ep["tags"][0],
        )
        if _ep:
            updates.append(
                ESIEndpointStatus(
                    date=time,
                    status=getattr(ESIStatus, ep["status"].upper()),
                    endpoint=_ep
                )
            )
    
    ESIEndpointStatus.objects.bulk_create(updates)

    DataProvider.set()
    DataProvider.get_set_page_cache()
