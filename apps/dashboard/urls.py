from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Auth
    path("login/", views.StaffLoginView.as_view(), name="login"),
    path("logout/", views.staff_logout, name="logout"),

    # Overview
    path("", views.overview, name="overview"),

    
    # Music
    path("music/", views.music_list, name="music_list"),
    path("music/add/", views.music_create, name="music_create"),
    path("music/<int:pk>/edit/", views.music_edit, name="music_edit"),
    path("music/<int:pk>/delete/", views.music_delete, name="music_delete"),

    # Events
    path("events/", views.event_list, name="event_list"),
    path("events/add/", views.event_create, name="event_create"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),

    # Users (admin only)
    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:user_id>/delete/", views.user_delete, name="user_delete"),
    path("users/<int:user_id>/toggle/", views.user_toggle_active, name="user_toggle"),
]