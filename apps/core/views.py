from django.shortcuts import render
from apps.core.models import ArtistProfile
from apps.events.models import Event
from apps.music.models import Mix

def home(request):
    artist = ArtistProfile.current()
    events = Event.objects.filter(is_published=True).order_by("start_at")[:3]
    mixes = Mix.objects.filter(is_published=True)[:3]

    videos = Mix.objects.filter(
        is_published=True,
        media_type="video"
    )
    audios = Mix.objects.filter(
        is_published=True,
        media_type="audio"
    )

    return render(
        request, "core/home.html",{
        "artist": artist, 
        "events": events,
        "mixes": mixes,
        "videos": videos,
        "audios": audios,
    })
