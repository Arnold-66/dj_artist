from django import forms

from .models import PressKit, PressImage


class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        attrs.pop("multiple", None)
        super().__init__(attrs)
        self.attrs["multiple"] = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, "getlist"):
            return files.getlist(name)
        return files.get(name)


class PressKitManagementForm(forms.ModelForm):
    """Edit the fields of an existing PressKit."""

    class Meta:
        model = PressKit
        fields = [
            "title",
            "slug",
            "hero_image",
            "short_bio",
            "full_bio",
            "technical_rider",
            "hospitality_rider",
            "stage_plot",
            "is_published",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "hero_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "short_bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "full_bio": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
            "technical_rider": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "hospitality_rider": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "stage_plot": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PressKitCreateForm(forms.ModelForm):
    class Meta:
        model = PressKit
        fields = ["title", "slug"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Summer 2025 Press Kit",
            }),
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "summer-2025",
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data["slug"]
        if PressKit.objects.filter(slug=slug).exists():
            raise forms.ValidationError("This slug is already used by another kit.")
        return slug


class PressImageUploadForm(forms.Form):
    images = forms.FileField(
        required=True,
        label="Choose press images",
        widget=MultipleFileInput(attrs={
            "class": "form-control",
            "accept": ".jpg,.jpeg,.png,.webp,image/*",
        }),
    )

    def clean_images(self):
        images = self.cleaned_data.get("images") or []
        if not images:
            raise forms.ValidationError("Please select at least one image.")
        return images


class PressImageSelectionForm(forms.Form):
    """
    Select which PressImages belong to this kit.
    Preserves the "checkbox list of all images" UX but writes via FK.
    """

    press_images = forms.ModelMultipleChoiceField(
        queryset=PressImage.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Images displayed in the public EPK",
    )

    def __init__(self, *args, kit=None, **kwargs):
        self.kit = kit
        super().__init__(*args, **kwargs)
        self.fields["press_images"].queryset = PressImage.objects.order_by("-created_at")
        if kit is not None:
            self.fields["press_images"].initial = list(
                kit.press_images.values_list("pk", flat=True)
            )

    def clean_press_images(self):
        return self.cleaned_data.get("press_images") or PressImage.objects.none()

    def save(self):
        """
        Attach selected images to this kit. Any image NOT selected is
        detached by reassigning it to... nothing? No — since FK is required,
        we can't detach. Instead, we DELETE images that were removed from
        this kit (they're exclusively owned by the kit in this model).
        """
        # NOTE: with a required FK, "deselect" means "delete from this kit."
        # If you want images to survive deselect, use a M2M instead. Keep
        # them as-is here; the UI should warn the user.
        selected = self.cleaned_data.get("press_images") or PressImage.objects.none()
        selected_ids = set(selected.values_list("pk", flat=True))

        # ensure selected images are attached to this kit
        PressImage.objects.filter(pk__in=selected_ids).update(kit=self.kit)

        # delete any image of this kit that is no longer selected
        self.kit.press_images.exclude(pk__in=selected_ids).delete()
        return selected


class PressImageEditForm(forms.ModelForm):
    class Meta:
        model = PressImage
        fields = ["title", "photographer_credit", "image", "order"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "photographer_credit": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }