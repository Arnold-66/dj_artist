from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

class Command(BaseCommand):
    help = "Send a test email to verify SMTP config"

    def add_arguments(self, parser):
        parser.add_argument("to", help="Recipient address")

    def handle(self, *args, **opts):
        to = opts["to"]
        self.stdout.write(f"Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Host:    {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        self.stdout.write(f"From:    {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"Sending to {to} ...")

        try:
            send_mail(
                subject="Test email from Django",
                message="If you can read this, SMTP works.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("Plain-text email sent ✔"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Plain-text FAILED: {e}"))
            return

        try:
            msg = EmailMultiAlternatives(
                subject="Test HTML email",
                body="Fallback plain text.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to],
            )
            msg.attach_alternative(
                "<h1>Hello!</h1><p>HTML email works.</p>", "text/html"
            )
            msg.send(fail_silently=False)
            self.stdout.write(self.style.SUCCESS("HTML email sent ✔"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"HTML FAILED: {e}"))