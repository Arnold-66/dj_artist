from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import ArtistProfile
from apps.events.models import Event
from apps.music.models import Mix
from apps.epk.models import PressKit

class Command(BaseCommand):
    help = "Load clearly labelled demo content for local development."
    def handle(self, *args, **options):
        ArtistProfile.objects.get_or_create(stage_name="DJ ARTIST", defaults={"tagline":"Global sound. Unforgettable nights.","short_bio":"Demo profile: replace this with the artist's approved biography.","full_bio":"DJ ARTIST is a demo artist profile. Replace this text with the real artist story, genres, notable performances and career highlights."})
        PressKit.objects.get_or_create(slug="official", defaults={"title":"Official Electronic Press Kit","is_public":True,"short_bio":"Demo EPK biography — replace with approved artist copy.","full_bio":"This is placeholder EPK copy. Add the artist's verified biography, notable shows, releases, style and press highlights."})
        now = timezone.now()
        demos = [("DEMO · Kampala Club Residency", "demo-kampala-club-residency", now+timedelta(days=7), "Kampala, Uganda"),("DEMO · Summer Festival Stage", "demo-summer-festival-stage", now+timedelta(days=28), "Nairobi, Kenya"),("DEMO · Private Brand Event", "demo-private-brand-event", now+timedelta(days=45), "Kigali, Rwanda")]
        for title, slug, start, place in demos:
            Event.objects.get_or_create(slug=slug, defaults={"title":title,"event_type":"Demo event — replace me","venue":"Demo venue","city_country":place,"start_at":start,"end_at":start+timedelta(hours=3),"description":"DEMO CONTENT ONLY. Replace or delete this event before publishing the real website.","is_published":True})
        mixes = [("DEMO · Opening Set", "youtube", "https://www.youtube.com/embed/ScMzIvxBSi4"),("DEMO · Deep House Session", "soundcloud", "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/293"),("DEMO · Afro House Selection", "audiomack", "https://audiomack.com/embed/song/demo/demo-track")]
        for title, platform, url in mixes:
            Mix.objects.get_or_create(title=title, defaults={"platform":platform,"embed_url":url,"description":"DEMO EMBED — replace with the artist's real link before launch.","is_published":True})
        self.stdout.write(self.style.SUCCESS("Demo content loaded. All demo events and mixes are labelled DEMO; replace or remove them before launch."))
