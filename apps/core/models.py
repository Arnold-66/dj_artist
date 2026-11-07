from django.db import models

class ArtistProfile(models.Model):
    stage_name = models.CharField(max_length=120, default="DJ ARTIST")
    tagline = models.CharField(max_length=200, blank=True, default="Music. Culture. Unforgettable Experiences.")
    short_bio = models.TextField(blank=True)
    full_bio = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="artist/", blank=True, null=True)
    logo = models.ImageField(upload_to="artist/", blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Artist profile"

    def __str__(self):
        return self.stage_name

    @classmethod
    def current(cls):
        return cls.objects.first()
