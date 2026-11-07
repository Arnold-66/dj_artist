from django import forms
from django.contrib.auth import get_user_model

from apps.bookings.models import BookingInquiry
from apps.music.models import Mix
from apps.events.models import Event

User = get_user_model()


# ---------- BOOKINGS ----------
class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = BookingInquiry
        fields = ["status"]
        widgets = {"status": forms.Select(attrs={"class": "form-select"})}


class BookingReplyForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Email subject"}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 7, "placeholder": "Write your reply..."}),
    )


# ---------- USERS ----------
class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Confirm Password")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "is_staff", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        if cleaned.get("password1") and len(cleaned["password1"]) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_staff = True
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="New Password (leave blank to keep current)",
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "is_staff", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("new_password")
        if pwd:
            if len(pwd) < 8:
                raise forms.ValidationError("Password must be at least 8 characters.")
            user.set_password(pwd)
        if commit:
            user.save()
        return user


# ---------- MUSIC ----------
class MixForm(forms.ModelForm):
    class Meta:
        model = Mix
        fields = [
            "title", "media_type", "platform", "embed_url",
            "audio_file", "cover_image", "description",
            "private_audio_file", "is_featured", "is_published",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "media_type": forms.Select(attrs={"class": "form-select"}),
            "platform": forms.TextInput(attrs={"class": "form-control"}),
            "embed_url": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "audio_file": forms.FileInput(attrs={"class": "form-control"}),
            "cover_image": forms.FileInput(attrs={"class": "form-control"}),
            "private_audio_file": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


# ---------- EVENTS ----------
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title", "slug", "event_type", "venue", "city_country",
            "start_at", "end_at", "description", "poster",
            "ticket_url", "is_published", "notify_subscribers",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "event_type": forms.TextInput(attrs={"class": "form-control"}),
            "venue": forms.TextInput(attrs={"class": "form-control"}),
            "city_country": forms.TextInput(attrs={"class": "form-control"}),
            "start_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "end_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "poster": forms.FileInput(attrs={"class": "form-control"}),
            "ticket_url": forms.URLInput(attrs={"class": "form-control"}),
        }