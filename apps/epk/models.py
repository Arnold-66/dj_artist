from django.db import models
from django.urls import reverse
from django.utils.text import slugify



class PressImage(models.Model):
    # no kit FK
    image = models.ImageField(upload_to="epk/press/")
    title = models.CharField(max_length=200, blank=True)
    photographer_credit = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or f"Press image #{self.pk}"

    
class PressKit(models.Model):
    # --- Core content ---
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=220)

    is_active = models.BooleanField(
        default=False,
        help_text="Only the active kit is shown at /epk/official/. "
                  "Activating a kit deactivates all others.",
    )
    
    short_bio = models.TextField(
        blank=True,
        help_text="Brief intro shown in the EPK hero.",
    )
    full_bio = models.TextField(
        blank=True,
        help_text="Full artist biography shown in the EPK body.",
    )

    press_images = models.ManyToManyField(
        PressImage, blank=True, related_name="kits",
    )

    # --- Hero image ---
    hero_image = models.ImageField(
        upload_to="epk/hero/",
        blank=True,
        null=True,
        help_text="Large background image for the EPK hero section. "
                  "If blank, the first press image is used.",
    )

    # --- Production files ---
    technical_rider = models.FileField(
        upload_to="epk/riders/", blank=True, null=True,
    )
    hospitality_rider = models.FileField(
        upload_to="epk/riders/", blank=True, null=True,
    )
    stage_plot = models.FileField(
        upload_to="epk/riders/", blank=True, null=True,
    )

    # --- Status / timestamps ---
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Press Kit"
        verbose_name_plural = "Press Kits"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "press-kit"
            slug = base
            n = 2
            while PressKit.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("epk:detail", kwargs={"slug": self.slug})

    @property
    def rider_slots(self):
        """(field_name, label, description) tuples for the template."""
        slots = []
        if self.technical_rider:
            slots.append((
                "technical",
                "Technical Rider",
                "Technical and equipment requirements.",
            ))
        if self.hospitality_rider:
            slots.append((
                "hospitality",
                "Hospitality Rider",
                "Hospitality and accommodation requirements.",
            ))
        if self.stage_plot:
            slots.append((
                "stage_plot",
                "Stage Plot",
                "Stage layout and performance setup.",
            ))
        return slots

