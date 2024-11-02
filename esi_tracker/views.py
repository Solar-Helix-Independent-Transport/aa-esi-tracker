"""App Views"""
from datetime import timedelta, datetime
from collections import OrderedDict

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect

from .models import ESIEndpointStatus
from .tasks import esi_status_snapshot
from .enums import ESIStatus
from .providers import DataProvider
from django.views.decorators.cache import cache_page


@cache_page(60*5)
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request:
    :return:
    """

    page = DataProvider.get_set_page_cache()
    return HttpResponse(page)

def index2(request: WSGIRequest) -> HttpResponse:
    if request.user.is_superuser:
        esi_status_snapshot.delay()
    return redirect("index")
