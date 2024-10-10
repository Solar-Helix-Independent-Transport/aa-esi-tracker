"""App Views"""
from datetime import timedelta, datetime
from collections import OrderedDict

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import redirect, render

from .models import ESIEndpointStatus
from .tasks import esi_status_snapshot
from .enums import ESIStatus

from django.views.decorators.cache import cache_page

@cache_page(60*5)
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    context = {"text": "Hello, World!"}
    start = timezone.now() - timedelta(hours=24*30)
    updates = ESIEndpointStatus.objects.filter(
        date__gte=start
    ).order_by(
        "endpoint__tag","endpoint__endpoint","date"
    ).select_related("endpoint")
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
                "last":start
            }
        d = u.date.strftime("%Y-%m-%d")
        if d not in data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"]:
                data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d] = {
                    "o": 0,
                    "t": 0,
                    "g": 0,
                    "y": 0,
                    "r": 0,
                }
        data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["t"] += 1
        if u.status == ESIStatus.RED:
             data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["r"] +=1
        elif  u.status == ESIStatus.YELLOW:
             data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["y"] +=1
        elif  u.status == ESIStatus.GREEN:
             data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["g"] +=1
        
        o = data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["o"]
        t = data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["t"]

        data[u.endpoint.tag]["endpoints"][u.endpoint.route]["updates"][d]["o"] = (o*(t-1)+u.status) / t

    context["data"] = data
    
    return render(request, "esi_tracker/index.html", context)

def index2(request: WSGIRequest) -> HttpResponse:

    esi_status_snapshot.delay()

    return redirect("/esi")
