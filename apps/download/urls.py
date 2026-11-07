from django.urls import path
from . import views

app_name = "downloads"

urlpatterns = [
    path("history/", views.download_history, name="history"),
]