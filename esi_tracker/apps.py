"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Example App
from esi_tracker import __version__


class ExampleConfig(AppConfig):
    """ESI Tracker App"""

    name = "esi_tracker"
    label = "esi_tracker"
    verbose_name = f"ESI Tracker v{__version__}"
