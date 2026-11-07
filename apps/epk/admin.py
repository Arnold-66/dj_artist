from django.contrib import admin
from .models import PressKit, PressImage


@admin.register(PressImage)
class PressImageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "created_at")
    list_editable = ("order",)
    search_fields = ("title", "photographer_credit")
    ordering = ("order", "id")


@admin.register(PressKit)
class PressKitAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "short_bio", "full_bio")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("press_images",)

    fieldsets = (
        ("Content", {
            "fields": ("title", "slug", "short_bio", "full_bio"),
        }),
        ("Images", {
            "fields": ("hero_image", "press_images"),
        }),
        ("Production files", {
            "fields": ("technical_rider", "hospitality_rider", "stage_plot"),
        }),
        ("Status", {
            "fields": ("is_published", "created_at", "updated_at"),
        }),
    )