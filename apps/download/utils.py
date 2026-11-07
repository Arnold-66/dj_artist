from django.utils import timezone
from .models import DownloadLog


def log_download(user, *, title, kind, reference_id=None, file_url="", request=None):
    ip = None
    if request:
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = (xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR"))
    DownloadLog.objects.create(
        user=user,
        title=title,
        kind=kind,
        reference_id=reference_id,
        file_url=file_url,
        ip_address=ip,
    )