"""Hook into Alliance Auth"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.services.hooks import UrlHook

from esi_tracker import urls


@hooks.register("url_hook")
def register_urls():
    """Register app urls"""

    return UrlHook(urls, "esit", r"^esit/", ["esi_tracker.views.index"])
