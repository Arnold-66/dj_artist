from django.urls import path
from . import views

app_name = "music"

urlpatterns = [
    path("", views.mix_list, name="list"),
    path("add/", views.mix_add, name="add"),
    path("<int:pk>/edit/", views.mix_edit, name="edit"),
    path("<int:pk>/delete/", views.mix_delete, name="delete"),
    path("<int:pk>/download/", views.mix_download, name="download"),
]