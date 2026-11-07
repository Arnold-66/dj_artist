from django.contrib import admin
from .models import Mix


@admin.register(Mix)
class MixAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "media_type",
        "platform",
        "is_featured",
        "is_published",
        "created_at",
    )

    list_filter = (
        "media_type",
        "platform",
        "is_featured",
        "is_published",
    )

    search_fields = ("title", "description")