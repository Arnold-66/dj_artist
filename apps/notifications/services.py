from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils import timezone
from apps.subscribers.models import Subscriber
from .models import EmailCampaign

def send_campaign(campaign):
    recipients = Subscriber.objects.filter(is_confirmed=True)
    if campaign.subject_type == "event": recipients = recipients.filter(events_opt_in=True)
    elif campaign.subject_type == "mix": recipients = recipients.filter(mixes_opt_in=True)
    messages = [(campaign.subject, campaign.message, settings.DEFAULT_FROM_EMAIL, [s.email]) for s in recipients]
    if messages:
        sent = send_mass_mail(messages, fail_silently=False)
    else: sent = 0
    campaign.recipient_count = sent
    campaign.sent_at = timezone.now()
    campaign.save(update_fields=["recipient_count", "sent_at"])
    return sent

def announce_new_content(kind, title, url):
    subject = f"New {kind}: {title}"
    message = f"A new {kind} has been posted by DJ ARTIST.\n\n{title}\n\nView it here: {url}\n\nYou are receiving this because you subscribed to updates."
    recipients = Subscriber.objects.filter(is_confirmed=True)
    if kind == "event": recipients = recipients.filter(events_opt_in=True)
    else: recipients = recipients.filter(mixes_opt_in=True)
    messages = [(subject, message, settings.DEFAULT_FROM_EMAIL, [s.email]) for s in recipients]
    if messages: send_mass_mail(messages, fail_silently=False)
    EmailCampaign.objects.create(subject_type=kind if kind in ("event", "mix") else "general", subject=subject, message=message, sent_at=timezone.now(), recipient_count=len(messages))
