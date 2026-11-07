from django.db import models
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from html.parser import HTMLParser
from django.conf import settings


private_audio_storage = FileSystemStorage(
    location=Path(settings.BASE_DIR) / "private_uploads"
)


class IframeSrcParser(HTMLParser):
    """Extract the src attribute from a pasted iframe."""

    def __init__(self):
        super().__init__()
        self.src = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "iframe":
            attributes = dict(attrs)
            self.src = attributes.get("src", "").strip()


class Mix(models.Model):

    MEDIA_TYPES = [
        ("video", "Video"),
        ("audio", "Audio"),
    ]

    title = models.CharField(max_length=180)

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPES,
        default="video"
    )

    platform = models.CharField(
        max_length=50,
        blank=True,
        help_text="YouTube, SoundCloud, Spotify, Audiomack, etc."
    )

    # TextField allows either a normal URL or complete iframe HTML.
    embed_url = models.TextField(
        blank=True,
        help_text=(
            "Paste the complete iframe HTML copied from Spotify, "
            "SoundCloud, YouTube, Audiomack, etc., or paste a normal URL. "
            "The website automatically extracts the iframe URL."
        )
    )

    audio_file = models.FileField(
        upload_to="music/audio/",
        blank=True,
        null=True,
        help_text="Optional public audio upload, such as an MP3."
    )

    video_file = models.FileField(
        upload_to="music/video/",
        blank=True,
        null=True,
        help_text="Optional public video upload, such as an MP4."
    )
    description = models.TextField(blank=True)

    cover_image = models.ImageField(
        upload_to="music/covers/",
        blank=True,
        null=True
    )

    private_audio_file = models.FileField(
        upload_to="audio_reference/",
        storage=private_audio_storage,
        blank=True,
        help_text="Private reference copy for the team only; it is not shown publicly."
    )

    spotify_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    audiomack_url = models.URLField(blank=True)
    soundcloud_url = models.URLField(blank=True)
    apple_music_url = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def get_embed_src(self):
        """
        Accept either:
        1. A normal platform URL.
        2. A complete iframe HTML snippet.

        Extract the iframe src and convert ordinary YouTube/Spotify
        links into their official embed URLs.
        """

        if not self.embed_url:
            return ""

        pasted_value = self.embed_url.strip()

        # If complete iframe HTML was pasted, extract its src.
        if "<iframe" in pasted_value.lower():
            parser = IframeSrcParser()

            try:
                parser.feed(pasted_value)
                url = parser.src
            except Exception:
                return ""
        else:
            url = pasted_value

        if not url:
            return ""

        parsed_url = urlparse(url)

        # Only allow HTTPS URLs.
        if parsed_url.scheme != "https" or not parsed_url.hostname:
            return ""

        hostname = parsed_url.hostname.lower().removeprefix("www.")

        # YouTube short links.
        if hostname == "youtu.be":
            video_id = parsed_url.path.strip("/").split("/")[0]

            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

            return ""

        # YouTube normal and embed links.
        if hostname in [
            "youtube.com",
            "m.youtube.com",
            "music.youtube.com"
        ]:
            if parsed_url.path == "/watch":
                video_id = parse_qs(parsed_url.query).get("v", [""])[0]

                if video_id:
                    return f"https://www.youtube.com/embed/{video_id}"

            elif parsed_url.path.startswith(
                ("/embed/", "/shorts/", "/live/")
            ):
                return url

            return ""

        # Convert normal Spotify track/album/playlist links.
        if hostname == "open.spotify.com":
            path_parts = parsed_url.path.strip("/").split("/")

            if len(path_parts) >= 2:
                if path_parts[0] in [
                    "track",
                    "album",
                    "playlist",
                    "episode",
                    "show"
                ]:
                    return (
                        f"https://open.spotify.com/embed/"
                        f"{path_parts[0]}/{path_parts[1]}"
                    )

                if path_parts[0] == "embed":
                    return url

            return ""

        # Approved platform embed domains.
        allowed_hosts = {
            "w.soundcloud.com",
            "audiomack.com",
        }

        extra_hosts = getattr(
            settings,
            "MUSIC_EMBED_ALLOWED_HOSTS",
            []
        )

        allowed_hosts.update(
            host.lower().removeprefix("www.")
            for host in extra_hosts
        )

        if hostname in allowed_hosts:
            return url

        return ""

    def get_embed_height(self):
        """Return a suitable display height for the platform."""

        platform_name = (self.platform or "").lower()

        if platform_name == "soundcloud":
            return 300

        if platform_name == "spotify":
            return 352

        if platform_name == "audiomack":
            return 300

        return 315



    @property
    def streaming_links(self):
        """Return list of (name, icon_class, url) for template rendering."""
        links = []
        if self.spotify_url:
            links.append(("Spotify", "fa-brands fa-spotify", self.spotify_url))
        if self.youtube_url:
            links.append(("YouTube", "fa-brands fa-youtube", self.youtube_url))
        if self.audiomack_url:
            links.append(("Audiomack", "fa-solid fa-music", self.audiomack_url))
        if self.soundcloud_url:
            links.append(("SoundCloud", "fa-brands fa-soundcloud", self.soundcloud_url))
        if self.apple_music_url:
            links.append(("Apple Music", "fa-brands fa-apple", self.apple_music_url))
        return links

    @property
    def duration_display(self):
        """Optional: store a duration string for display; skip if unknown."""
        return getattr(self, "duration", "")

    def __str__(self):
        return self.title