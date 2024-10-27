
from collections import OrderedDict
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from esi_tracker.enums import ESIStatus
from esi_tracker.models import ESIEndpointStatus

def build_dict():
    start = timezone.now() - timedelta(hours=24*14)
    updates = ESIEndpointStatus.objects.filter(
        date__gte=start
    ).select_related("endpoint").order_by(
        "endpoint__tag",
        "endpoint__route"
    )
    data = OrderedDict()
    for u in updates:
        if u.endpoint.tag not in data:
            data[u.endpoint.tag] = {
                "name": u.endpoint.tag,
                "endpoints": OrderedDict()
            }
        if u.endpoint.route not in data[u.endpoint.tag]["endpoints"]:
            data[u.endpoint.tag]["endpoints"][u.endpoint.route]={
                "updates":OrderedDict(),
                "first":timezone.now(),
                "last":start,
                "o":0,
                "t":0
            }
        d = u.date.strftime("%Y-%m-%d %H:00")
        if d not in data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"]:
                data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d] = {
                    "o": 0,
                    "t": 0,
                    "g": 0,
                    "y": 0,
                    "r": 0,
                }

        if data[u.endpoint.tag]["endpoints"][u.endpoint.route]["first"] > u.date:
            data[u.endpoint.tag]["endpoints"][u.endpoint.route]["first"] = u.date
        if data[u.endpoint.tag]["endpoints"][u.endpoint.route]["last"] < u.date:
            data[u.endpoint.tag]["endpoints"][u.endpoint.route]["last"] = u.date
             
        if u.status == ESIStatus.RED:
            data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["r"] +=1
        elif  u.status == ESIStatus.YELLOW:
            data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["y"] +=1
        elif  u.status == ESIStatus.GREEN:
            data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["g"] +=1
        
        data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["t"] += 1
        o = data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["o"]
        t = data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["t"]
        data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["o"] = (o*(t-1)+u.status) / t

        data[u.endpoint.tag]["endpoints"][u.endpoint.route]["t"] += 1
        o = data[u.endpoint.tag]["endpoints"][u.endpoint.route]["o"]
        t = data[u.endpoint.tag]["endpoints"][u.endpoint.route]["t"]
        data[u.endpoint.tag]["endpoints"][u.endpoint.route]["o"] = (o*(t-1)+u.status) / t

    return data


class DataProvider:
    timeout = 60*60  # 1h

    @classmethod
    def cache_tag():
        return "esi_tracker_data"
    
    @classmethod
    def get(cls):
        return cache.get(cls.cache_tag, lambda: build_dict())
    
    @classmethod
    def set(cls):
        cache.set(cls.cache_tag, build_dict(), cls.timeout)
