"""App URLs"""

# Django
from django.urls import path

# AA Example App
from . import views

app_name: str = "esit"

urlpatterns = [
    path("", views.index, name="index"),
    path("recent", views.hourly, name="hourly"),
    path("recent/<int:hours>/", views.hourly, name="hourly_short"),
    path("rt", views.index2, name="runtask"),
]
