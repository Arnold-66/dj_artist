from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "slug",
            "event_type",
            "venue",
            "city_country",
            "start_at",
            "end_at",
            "description",
            "poster",
            "ticket_url",
            "is_published",
            "notify_subscribers",
        ]
        widgets = {
            "start_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make datetime inputs render with the correct initial value
        self.fields["start_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        if self.instance and self.instance.pk:
            if self.instance.start_at:
                self.initial["start_at"] = self.instance.start_at.strftime("%Y-%m-%dT%H:%M")
            if self.instance.end_at:
                self.initial["end_at"] = self.instance.end_at.strftime("%Y-%m-%dT%H:%M")