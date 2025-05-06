import logging

from collections import OrderedDict
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from esi_tracker.enums import ESIStatus
from esi_tracker.models import ESIEndpointStatus
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

DEFAULT_LOOKBACK = 24*14
DEFAULT_DATESTRING = "%Y-%m-%d %H:00"
def build_dict(hours=DEFAULT_LOOKBACK, date_string=DEFAULT_DATESTRING):
    logger.info("Rebuilding dict")
    start = timezone.now() - timedelta(hours=hours)
    now = timezone.now()
    updates = ESIEndpointStatus.objects.filter(
        date__gte=start
    ).select_related("endpoint").order_by(
        "endpoint__tag",
        "endpoint__route"
    ).values(
        "endpoint__tag",
        "endpoint__method",
        "endpoint__route",
        "date",
        "status"
    )
    logger.info(f"Events {updates.count()}")
    data = OrderedDict()
    for u in updates:
        if u['endpoint__tag'] not in data:
            data[u['endpoint__tag']] = {
                "name": u['endpoint__tag'],
                "endpoints": OrderedDict()
            }
        route = f"{u['endpoint__method']} - {u['endpoint__route']}"
        if route not in data[u['endpoint__tag']]["endpoints"]:
            data[u['endpoint__tag']]["endpoints"][route]={
                "updates":OrderedDict(),
                "first":now,
                "last":start,
                "o":0,
                "t":0
            }
        d = u['date'].strftime(date_string)
        if d not in data[u['endpoint__tag']]["endpoints"][route]["updates"]:
                data[u['endpoint__tag']]["endpoints"][route]["updates"][d] = {
                    "o": 0,
                    "t": 0,
                    "g": 0,
                    "y": 0,
                    "r": 0,
                }
        if data[u['endpoint__tag']]["endpoints"][route]["first"] > u['date']:
            data[u['endpoint__tag']]["endpoints"][route]["first"] = u['date']
        if data[u['endpoint__tag']]["endpoints"][route]["last"] < u['date']:
            data[u['endpoint__tag']]["endpoints"][route]["last"] = u['date']
        if u['status'] == ESIStatus.RED:
            data[u['endpoint__tag']]["endpoints"][route]["updates"][d]["r"] +=1
        elif  u['status'] == ESIStatus.YELLOW:
            data[u['endpoint__tag']]["endpoints"][route]["updates"][d]["y"] +=1
        elif  u['status'] == ESIStatus.GREEN:
            data[u['endpoint__tag']]["endpoints"][route]["updates"][d]["g"] +=1
        data[u['endpoint__tag']]["endpoints"][route]["updates"][d]["t"] += 1
        o = data[u['endpoint__tag']]["endpoints"][route]["updates"][d]["o"]
        t = data[u['endpoint__tag']]["endpoints"][route]["updates"][d]["t"]
        data[u['endpoint__tag']]["endpoints"][route]["updates"][d]["o"] = (o*(t-1)+u['status']) / t
        data[u['endpoint__tag']]["endpoints"][route]["t"] += 1
        o = data[u['endpoint__tag']]["endpoints"][route]["o"]
        t = data[u['endpoint__tag']]["endpoints"][route]["t"]
        data[u['endpoint__tag']]["endpoints"][route]["o"] = (o*(t-1)+u['status']) / t
    logger.info("Finished dict")
    return data


class DataProvider:
    timeout = 60*60  # 1h

    @classmethod
    def cache_tag():
        return "esi_tracker_data"
    
    @classmethod
    def get(cls):
        logger.info("Fetching Fresh Data from Database")
        return cache.get(cls.cache_tag, lambda: build_dict())
    
    @classmethod
    def set(cls):
        logger.info("Saving Fresh Data to cache from database")
        cache.set(cls.cache_tag, build_dict(), cls.timeout)

    @classmethod
    def get_set_page_cache(cls):
        logger.info("Getting Page Cache")

        page = cache.get(f"{cls.cache_tag}_html")
        if not page:
            logger.info("No Page Cache")
            return cls.set_page_cache()
        logger.info("Found Page Cache")
        return page
    
    @classmethod
    def set_page_cache(cls):
        logger.info("Setting Page Cache")

        data = cls.get()
        context = {"text": "Last 14days"}
        context["data"] = data

        rendered = render_to_string("esi_tracker/index.html", context)

        cache.set(f"{cls.cache_tag}_html", rendered, cls.timeout)
        logger.info("Completed Set Page Cache")
        return rendered
