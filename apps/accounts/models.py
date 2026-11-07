from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_OPERATOR = "operator"
    ROLE_KIT_USER = "kit_user"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Administrator"),
        (ROLE_OPERATOR, "Operator"),
        (ROLE_KIT_USER, "Press Kit User"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_KIT_USER,
    )

    # Auto-subscribe on registration
    is_subscribed = models.BooleanField(
        default=True,
        help_text="Auto-subscribed on registration; user can unsubscribe anytime.",
    )
    subscribed_at = models.DateTimeField(default=timezone.now, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["username"]

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_operator_role(self):
        return self.role == self.ROLE_OPERATOR

    @property
    def is_kit_user(self):
        return self.role == self.ROLE_KIT_USER

    @property
    def can_download(self):
        """Only verified accounts (staff bypass; kit users need verified email)."""
        if self.is_staff or self.is_superuser:
            return True
        return self.is_active and self.emailaddress_set.filter(verified=True).exists()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"