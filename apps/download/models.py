from django.conf import settings
from django.db import models


class DownloadLog(models.Model):
    KIND_AUDIO = "audio"
    KIND_VIDEO = "video"
    KIND_EPK = "epk"

    KIND_CHOICES = [
        (KIND_AUDIO, "Audio"),
        (KIND_VIDEO, "Video"),
        (KIND_EPK, "Press Kit File"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="download_logs",
    )
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    file_url = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.title}"