from django.contrib import admin
from .models import ArtistProfile
@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ("stage_name", "email", "updated_at")
