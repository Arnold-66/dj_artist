from django.db import models
from django.conf import settings


class BookingInquiry(models.Model):
    EVENT_TYPES = [
        ("corporate", "Corporate"),
        ("festival", "Festival"),
        ("club", "Club"),
        ("private", "Private"),
        ("other", "Other"),
    ]
    STATUSES = [
        ("new", "New"),
        ("reviewing", "Under review"),
        ("negotiation", "Negotiation"),
        ("confirmed", "Confirmed"),
        ("declined", "Declined"),
    ]

    organization = models.CharField(max_length=180)
    contact_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    # NEW: free-text description when event_type == "other"
    other_event_type = models.CharField(
        max_length=180,
        blank=True,
        help_text="If you selected 'Other', describe your event type.",
    )
    event_name = models.CharField(max_length=180, blank=True)
    event_date = models.DateField()
    venue = models.CharField(max_length=180, blank=True)
    city_country = models.CharField(max_length=180)
    audience_size = models.PositiveIntegerField(null=True, blank=True)
    budget = models.CharField(
        max_length=100, blank=True,
        help_text="Include currency, e.g. USD 2,000"
    )
    performance_duration = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUSES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization} - {self.event_type} ({self.event_date})"

    # ---- Small helpers used by templates ----
    @property
    def status_display(self):
        return self.get_status_display()

    @property
    def event_type_display(self):
        # If "other", show the custom label the user typed.
        if self.event_type == "other" and self.other_event_type:
            return self.other_event_type
        return self.get_event_type_display()


class BookingReply(models.Model):
    EMAIL_STATUSES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    booking = models.ForeignKey(
        "bookings.BookingInquiry",
        on_delete=models.CASCADE,
        related_name="replies",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking_replies",
    )
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    email_status = models.CharField(
        max_length=20, choices=EMAIL_STATUSES, default="pending"
    )
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Booking Reply"
        verbose_name_plural = "Booking Replies"

    def __str__(self):
        return (
            f"Reply to {self.booking.contact_name} "
            f"- {self.get_email_status_display()}"
        )