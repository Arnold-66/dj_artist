from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    event_type = models.CharField(max_length=80, default="Live performance")
    venue = models.CharField(max_length=180, blank=True)
    city_country = models.CharField(max_length=180)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    poster = models.ImageField(upload_to="events/posters/", blank=True, null=True)
    ticket_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    notify_subscribers = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_at"]

    def __str__(self):
        return self.title
