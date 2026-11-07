from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list, name="list"),

    # Management routes (must come BEFORE the <slug> catch-all)
    path("add/", views.event_create, name="create"),

    # Detail + edit/delete + calendar
    path("<slug:slug>/", views.event_detail, name="detail"),
    path("<slug:slug>/edit/", views.event_update, name="update"),
    path("<slug:slug>/delete/", views.event_delete, name="delete"),
    path("<slug:slug>/calendar.ics", views.event_calendar, name="calendar"),
]