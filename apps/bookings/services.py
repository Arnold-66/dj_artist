import os

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import BookingReply


# ---------------------------------------------------------------------
# Public booking notification (sent to the admin/team)
# ---------------------------------------------------------------------
def notify_new_booking(inquiry):
    """
    Send a notification email about a new booking inquiry to the
    address configured in BOOKING_NOTIFICATION_EMAIL (falls back to
    DEFAULT_FROM_EMAIL).
    """
    recipient = (
        os.getenv("BOOKING_NOTIFICATION_EMAIL")
        or settings.DEFAULT_FROM_EMAIL
    )

    try:
        send_mail(
            subject=f"New booking inquiry: {inquiry.organization}",
            message=(
                f"New {inquiry.event_type_display} inquiry "
                f"for {inquiry.event_date}.\n\n"
                f"Contact: {inquiry.contact_name}, {inquiry.email}.\n"
                f"Location: {inquiry.city_country}.\n"
                f"Budget: {inquiry.budget or 'Not provided'}.\n\n"
                f"Message:\n{inquiry.message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True,
        )
    except Exception:
        # Notifications are best-effort — never block the inquiry.
        pass


# ---------------------------------------------------------------------
# NEW: Confirmation email sent to the person who submitted the inquiry
# ---------------------------------------------------------------------
def send_booking_confirmation(inquiry):
    """
    Send a confirmation email to the person who submitted the inquiry,
    letting them know their booking inquiry was received.

    Best-effort: failures never block the public user's flow.
    """
    try:
        send_mail(
            subject="We received your booking inquiry — DJ ARTIST",
            message=(
                f"Hi {inquiry.contact_name},\n\n"
                f"Thank you for reaching out to DJ ARTIST. "
                f"We have received your booking inquiry and the "
                f"management team will get back to you shortly.\n\n"
                f"Here is a summary of what you sent us:\n"
                f"-----------------------------------------\n"
                f"Organization : {inquiry.organization}\n"
                f"Event type   : {inquiry.event_type_display}\n"
                f"Event name   : {inquiry.event_name or '-'}\n"
                f"Event date   : {inquiry.event_date}\n"
                f"Venue        : {inquiry.venue or '-'}\n"
                f"Location     : {inquiry.city_country}\n"
                f"Audience     : "
                f"{inquiry.audience_size or 'Not provided'}\n"
                f"Budget       : {inquiry.budget or 'Not provided'}\n"
                f"Duration     : "
                f"{inquiry.performance_duration or 'Not provided'}\n"
                f"-----------------------------------------\n\n"
                f"Your message:\n{inquiry.message}\n\n"
                f"If you need to add anything, simply reply to this email.\n\n"
                f"— DJ ARTIST Management"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.email],
            fail_silently=True,
        )
    except Exception:
        # Best-effort — never block the inquiry.
        pass


# ---------------------------------------------------------------------
# Staff reply to a booking inquiry
# ---------------------------------------------------------------------
def send_booking_reply(booking, sender, subject, message):
    """
    Save a BookingReply and attempt to send the email.
    Returns the saved BookingReply with email_status set to
    'sent' or 'failed'.
    """
    reply = BookingReply.objects.create(
        booking=booking,
        sender=sender,
        recipient=booking.email,
        subject=subject,
        message=message,
        email_status="pending",
    )

    try:
        sent_count = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            fail_silently=False,
        )

        if sent_count != 1:
            raise RuntimeError(
                "The email backend did not confirm sending the email."
            )

        reply.email_status = "sent"
        reply.sent_at = timezone.now()
        reply.error_message = ""

    except Exception as error:
        reply.email_status = "failed"
        reply.error_message = str(error)

    reply.save(
        update_fields=["email_status", "sent_at", "error_message"]
    )

    return reply