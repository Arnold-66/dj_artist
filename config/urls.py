from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),

    path("", include("apps.core.urls")),
    path("bookings/", include("apps.bookings.urls")),
    path("epk/", include("apps.epk.urls")),
    path("music/", include("apps.music.urls")),
    path("events/", include("apps.events.urls")),
    path("subscribe/", include("apps.subscribers.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("download/", include("apps.download.urls")),
]

if settings.DEBUG:
    # Media files
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    # Static files (runserver usually serves these automatically,
    # but this is a safety net for DEBUG mode)
    if getattr(settings, "STATIC_URL", None):
        urlpatterns += static(
            settings.STATIC_URL,
            document_root=getattr(settings, "STATIC_ROOT", None),
        )