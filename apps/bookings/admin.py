from django.contrib import admin
from .models import BookingInquiry
@admin.register(BookingInquiry)
class BookingInquiryAdmin(admin.ModelAdmin):
    list_display = ("organization", "contact_name", "event_type", "event_date", "status", "created_at")
    list_filter = ("status", "event_type", "event_date")
    search_fields = ("organization", "contact_name", "email", "city_country")
    readonly_fields = ("created_at",)
