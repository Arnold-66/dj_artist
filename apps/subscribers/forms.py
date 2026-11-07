from django import forms
from .models import Subscriber

class SubscribeForm(forms.ModelForm):
    consent = forms.BooleanField(required=True, label="I agree to receive email updates and understand I can unsubscribe at any time.")
    class Meta:
        model = Subscriber
        fields = ["name", "email", "events_opt_in", "mixes_opt_in"]
        widgets = {"events_opt_in": forms.CheckboxInput(), "mixes_opt_in": forms.CheckboxInput()}
