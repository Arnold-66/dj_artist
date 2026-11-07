from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.conf import settings
from .models import Event
from apps.notifications.services import announce_new_content
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_at", "city_country", "is_published", "notify_subscribers")
    list_filter = ("is_published", "event_type")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "venue", "city_country")
    def save_model(self, request, obj, form, change):
        was_published = Event.objects.filter(pk=obj.pk, is_published=True).exists() if change else False
        super().save_model(request, obj, form, change)
        if obj.is_published and obj.notify_subscribers and not was_published:
            try:
                announce_new_content("event", obj.title, f"{settings.SITE_URL}{reverse('events:detail', args=[obj.slug])}")
                messages.success(request, "Event published and subscriber email sent.")
            except Exception as exc: messages.error(request, f"Event saved, but email sending failed: {exc}")
