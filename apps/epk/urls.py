from django.urls import path
from . import views

app_name = "epk"

urlpatterns = [
    # ---------- Public ----------
    path("official/", views.press_kit, {"slug": "official"}, name="official"),

    # ---------- Management (MUST come before <slug:slug>) ----------
    path("manage/", views.kits_index, name="kits_index"),
    path("manage/create/", views.create_kit, name="create_kit"),
    path("manage/<int:kit_id>/", views.manage_epk, name="manage"),
    path("manage/<int:kit_id>/delete/", views.delete_kit, name="delete_kit"),
    path(
        "manage/<int:kit_id>/upload-images/",
        views.upload_press_images,
        name="upload_images",
    ),
    path(
        "manage/<int:kit_id>/activate/",
        views.activate_kit,
        name="activate_kit",
    ),
    path(
        "manage/<int:kit_id>/update-images/",
        views.update_epk_images,
        name="update_images",
    ),
    path(
        "manage/<int:kit_id>/image/<int:image_id>/remove/",
        views.remove_epk_image,
        name="remove_image",
    ),
    path(
        "manage/<int:kit_id>/image/<int:image_id>/edit/",
        views.edit_press_image,
        name="edit_image",
    ),
    path(
        "manage/<int:kit_id>/image/<int:image_id>/delete/",
        views.delete_press_image,
        name="delete_image",
    ),

    # ---------- Gated downloads (kit users, verified email only) ----------
    path(
        "<int:kit_id>/download/<str:which>/",
        views.rider_download,
        name="rider_download",
    ),
    path(
        "<int:kit_id>/image/<int:image_id>/download/",
        views.press_image_download,
        name="press_image_download",
    ),

    # ---------- Public catch-all — MUST be LAST ----------
    path("<slug:slug>/", views.press_kit, name="detail"),
]