from django import forms
from .models import BookingInquiry


class BookingInquiryForm(forms.ModelForm):
    """Public-facing booking form."""

    class Meta:
        model = BookingInquiry
        fields = [
            "organization", "contact_name", "email", "phone",
            "event_type", "other_event_type", "event_name",
            "event_date", "venue", "city_country", "audience_size",
            "budget", "performance_duration", "message",
        ]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 5}),
            "event_type": forms.Select(
                attrs={"id": "id_event_type", "class": "form-select"}
            ),
            "other_event_type": forms.TextInput(
                attrs={
                    "id": "id_other_event_type",
                    "class": "form-control",
                    "placeholder": "e.g. Wedding, Brand launch, etc.",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        event_type = cleaned_data.get("event_type")
        other_event_type = (cleaned_data.get("other_event_type") or "").strip()

        # If "Other" is selected, require a description.
        if event_type == "other" and not other_event_type:
            self.add_error(
                "other_event_type",
                "Please describe your event type when you select 'Other'.",
            )

        # If NOT "Other", clear the field (keeps data clean).
        if event_type != "other":
            cleaned_data["other_event_type"] = ""

        return cleaned_data


class BookingStatusForm(forms.ModelForm):
    """Staff: change a booking's status."""

    class Meta:
        model = BookingInquiry
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class BookingReplyForm(forms.Form):
    """Staff: reply to a booking inquiry by email."""

    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Email subject"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 7,
                "placeholder": "Write your reply...",
            }
        ),
    )