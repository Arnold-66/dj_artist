from django.contrib import admin
from .models import Subscriber
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "is_confirmed", "events_opt_in", "mixes_opt_in", "created_at")
    list_filter = ("is_confirmed", "events_opt_in", "mixes_opt_in")
    search_fields = ("email", "name")
