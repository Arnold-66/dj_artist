from django import forms
from .models import Mix


class MixForm(forms.ModelForm):
    class Meta:
        model = Mix
        fields = [
            "title",
            "media_type",
            "platform",
            "embed_url",
            "video_file",
            "audio_file",
            "description",
            "cover_image",
            "private_audio_file",
            "is_featured",
            "is_published",
            "spotify_url",
            "youtube_url",
            "audiomack_url",
            "soundcloud_url",
            "apple_music_url",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "embed_url": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned = super().clean()
        media_type = cleaned.get("media_type")
        embed_url = cleaned.get("embed_url")
        video_file = cleaned.get("video_file")
        audio_file = cleaned.get("audio_file")
        instance = self.instance
        existing_video = video_file or (instance.pk and instance.video_file)
        existing_audio = audio_file or (instance.pk and instance.audio_file)

        if media_type == "video" and not (embed_url or existing_video):
            raise forms.ValidationError(
                "For a video, provide either a YouTube embed URL or upload a video file."
            )
        if media_type == "audio" and not (embed_url or existing_audio):
            raise forms.ValidationError(
                "For audio, provide either an embed URL or upload an audio file."
            )
        return cleaned