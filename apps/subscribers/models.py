import uuid
from django.db import models

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120, blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_confirmed = models.BooleanField(default=False)
    events_opt_in = models.BooleanField(default=True)
    mixes_opt_in = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
