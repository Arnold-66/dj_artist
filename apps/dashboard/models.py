from django.db import models
from django.conf import settings


class AuditLog(models.Model):

    ACTIONS = [
        ("create", "Created"),
        ("update", "Updated"),
        ("delete", "Deleted"),
        ("login", "Logged in"),
        ("logout", "Logged out"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="management_activity"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTIONS
    )

    app_label = models.CharField(max_length=100)

    model_name = models.CharField(max_length=100)

    object_id = models.CharField(
        max_length=100,
        blank=True
    )

    object_repr = models.CharField(
        max_length=255,
        blank=True
    )

    changes = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Management Activity"
        verbose_name_plural = "Management Activities"

    def __str__(self):
        username = self.actor.username if self.actor else "Unknown user"

        return (
            f"{username} - {self.get_action_display()} "
            f"{self.model_name}: {self.object_repr}"
        )