from django.urls import path
from . import views
app_name = "subscribers"
urlpatterns = [
    path("", views.subscribe, name="subscribe"),
    path("confirm/<uuid:token>/", views.confirm, name="confirm"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe, name="unsubscribe"),
]
