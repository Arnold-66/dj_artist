from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import EmailCampaign
from .services import send_campaign
@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ("subject", "subject_type", "recipient_count", "sent_at", "created_at")
    readonly_fields = ("sent_at", "recipient_count")
    def get_urls(self):
        return [path("<int:campaign_id>/send/", self.admin_site.admin_view(self.send_view), name="notifications_emailcampaign_send")] + super().get_urls()
    def send_view(self, request, campaign_id):
        campaign = get_object_or_404(EmailCampaign, pk=campaign_id)
        if request.method == "POST":
            if campaign.sent_at:
                self.message_user(request, "This campaign has already been sent.", level=messages.WARNING)
            else:
                try:
                    count = send_campaign(campaign)
                    self.message_user(request, f"Campaign sent to {count} subscriber(s).", level=messages.SUCCESS)
                except Exception as exc: self.message_user(request, f"Sending failed: {exc}", level=messages.ERROR)
            return redirect("admin:notifications_emailcampaign_changelist")
        return TemplateResponse(request, "admin/send_campaign.html", {**self.admin_site.each_context(request), "campaign": campaign, "opts": self.model._meta})
