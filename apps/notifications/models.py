from django.db import models

class EmailCampaign(models.Model):
    SUBJECT_TYPES = [("event", "Event announcement"), ("mix", "New mix"), ("general", "General update")]
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default="general")
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)
    recipient_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
