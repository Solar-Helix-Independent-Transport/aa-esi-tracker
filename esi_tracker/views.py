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
from .providers import DataProvider
from django.views.decorators.cache import cache_page


# @cache_page(60*4.9)
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    context = {"text": "Hello, World!"}
    context["data"] = DataProvider.get()
    
    return render(request, "esi_tracker/index.html", context)

def index2(request: WSGIRequest) -> HttpResponse:

    esi_status_snapshot.delay()

    return redirect("/esi")
