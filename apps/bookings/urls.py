from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    # Public
    path("", views.booking_create, name="create"),

    # Staff
    path("manage/", views.bookings_list, name="bookings_list"),
    path(
        "manage/<int:booking_id>/",
        views.booking_detail,
        name="booking_detail",
    ),
]