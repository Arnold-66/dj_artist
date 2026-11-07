import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import PressKit, PressImage
from .forms import (
    PressKitManagementForm,
    PressKitCreateForm,
    PressImageUploadForm,
    PressImageSelectionForm,
    PressImageEditForm,
)
from django.urls import reverse

from apps.dashboard.models import AuditLog


def is_management_user(user):
    return user.is_authenticated and user.is_active and user.is_staff



def activate_kit(request, kit_id):
    if request.method != "POST":
        return redirect("epk:kits_index")

    kit = get_object_or_404(PressKit, pk=kit_id)

    with transaction.atomic():
        # Deactivate all others, activate this one
        PressKit.objects.exclude(pk=kit.pk).update(is_active=False)
        if not kit.is_active:
            kit.is_active = True
            kit.save(update_fields=["is_active"])

        AuditLog.objects.create(
            actor=request.user,
            action="update",
            app_label="epk",
            model_name="PressKit",
            object_id=str(kit.pk),
            object_repr=str(kit),
            changes={"activated_kit": kit.title},
        )

    messages.success(request, f'"{kit.title}" is now the active press kit.')
    return redirect("epk:kits_index")


# --------------------------------------------------
# PUBLIC EPK
# --------------------------------------------------

def press_kit(request, slug):
    # /epk/official/ → show the active kit (or the one actually named "official")
    if slug == "official":
        kit = PressKit.objects.filter(
            is_active=True, is_published=True
        ).first() or get_object_or_404(
            PressKit.objects.prefetch_related("press_images"),
            slug="official",
            is_published=True,
        )
    else:
        kit = get_object_or_404(
            PressKit.objects.prefetch_related("press_images"),
            slug=slug,
            is_published=True,
        )

    can_download = (
        request.user.is_authenticated
        and getattr(request.user, "can_download", False)
    )
    return render(request, "epk/detail.html", {
        "kit": kit,
        "can_download": can_download,
    })

# --------------------------------------------------
# KITS INDEX
# --------------------------------------------------

@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def kits_index(request):
    kits = PressKit.objects.all()
    return render(request, "epk/kits_index.html", {"kits": kits})


# --------------------------------------------------
# CREATE KIT
# --------------------------------------------------

@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def create_kit(request):
    if request.method == "POST":
        form = PressKitCreateForm(request.POST)
        if form.is_valid():
            kit = form.save()

            AuditLog.objects.create(
                actor=request.user,
                action="create",
                app_label="epk",
                model_name="PressKit",
                object_id=str(kit.pk),
                object_repr=str(kit),
                changes={"created_kit": kit.title, "slug": kit.slug},
            )

            messages.success(request, f'Press kit "{kit.title}" created.')
            return redirect("epk:manage", kit_id=kit.pk)
    else:
        form = PressKitCreateForm()

    return render(request, "epk/create_kit.html", {"form": form})


# --------------------------------------------------
# DELETE KIT
# --------------------------------------------------

@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def delete_kit(request, kit_id):
    if request.method != "POST":
        return redirect("epk:kits_index")

    kit = get_object_or_404(PressKit, pk=kit_id)
    title, pk = kit.title, kit.pk

    with transaction.atomic():
        # With M2M, `.clear()` detaches — safe. With FK, `.delete()` removes images.
        if hasattr(kit, "press_images"):
            try:
                kit.press_images.clear()
            except AttributeError:
                kit.press_images.all().delete()
        kit.delete()

        AuditLog.objects.create(
            actor=request.user,
            action="delete",
            app_label="epk",
            model_name="PressKit",
            object_id=str(pk),
            object_repr=title,
            changes={"deleted_kit": title},
        )

    messages.success(request, f'Press kit "{title}" deleted.')
    return redirect("epk:kits_index")


# --------------------------------------------------
# EPK MANAGEMENT (per-kit)
# --------------------------------------------------

@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def manage_epk(request, kit_id):
    kit = get_object_or_404(PressKit, pk=kit_id)

    if request.method == "POST":
        form = PressKitManagementForm(request.POST, request.FILES, instance=kit)

        if form.is_valid():
            old_values = {
                "title": kit.title,
                "is_published": kit.is_published,
                "short_bio": kit.short_bio,
                "full_bio": kit.full_bio,
            }

            with transaction.atomic():
                kit = form.save()

                AuditLog.objects.create(
                    actor=request.user,
                    action="update",
                    app_label="epk",
                    model_name="PressKit",
                    object_id=str(kit.pk),
                    object_repr=str(kit),
                    changes={
                        "before": old_values,
                        "after": {
                            "title": kit.title,
                            "is_published": kit.is_published,
                            "short_bio": kit.short_bio,
                            "full_bio": kit.full_bio,
                        },
                    },
                )

            messages.success(request, "Your Electronic Press Kit has been updated.")
            return redirect("epk:manage", kit_id=kit.pk)
    else:
        form = PressKitManagementForm(instance=kit)

    upload_form = PressImageUploadForm()

    all_images = PressImage.objects.order_by("-created_at")
    edit_forms = {
        photo.pk: PressImageEditForm(instance=photo, prefix=f"img{photo.pk}")
        for photo in all_images
    }
    selected_image_ids = set(kit.press_images.values_list("pk", flat=True))

    return render(
        request,
        "epk/manage.html",
        {
            "kit": kit,
            "form": form,
            "upload_form": upload_form,
            "press_images": all_images,
            "edit_forms": edit_forms,
            "selected_image_ids": selected_image_ids,
        },
    )


# --------------------------------------------------
# UPLOAD PRESS IMAGES
# --------------------------------------------------

@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def upload_press_images(request, kit_id):
    if request.method != "POST":
        return redirect("epk:manage", kit_id=kit_id)

    kit = get_object_or_404(PressKit, pk=kit_id)
    form = PressImageUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        for error in form.errors.get("images", []):
            messages.error(request, error)
        return redirect("epk:manage", kit_id=kit.pk)

    uploaded_images = form.cleaned_data["images"]
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    created_images = []

    for uploaded_file in uploaded_images:
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in allowed_extensions:
            messages.warning(
                request,
                f"{uploaded_file.name} was skipped. Use JPG, JPEG, PNG or WEBP.",
            )
            continue

        # M2M path:
        if hasattr(kit, "press_images") and hasattr(kit.press_images, "add"):
            photo = PressImage.objects.create(
                title=os.path.splitext(uploaded_file.name)[0][:120],
                image=uploaded_file,
            )
            kit.press_images.add(photo)
        else:
            # FK path
            photo = PressImage.objects.create(
                kit=kit,
                title=os.path.splitext(uploaded_file.name)[0][:120],
                image=uploaded_file,
            )

        created_images.append(photo)

    if created_images:
        AuditLog.objects.create(
            actor=request.user,
            action="create",
            app_label="epk",
            model_name="PressImage",
            object_id=",".join(str(p.pk) for p in created_images),
            object_repr=f"{len(created_images)} press image(s) uploaded",
            changes={"uploaded_images": [p.title for p in created_images]},
        )
        messages.success(
            request,
            f"{len(created_images)} press image(s) uploaded and added to this EPK.",
        )
    else:
        messages.error(
            request,
            "No valid images were uploaded. Use JPG, JPEG, PNG or WEBP.",
        )

    return redirect("epk:manage", kit_id=kit.pk)


# --------------------------------------------------
# VISIBILITY (which images appear in the public EPK)
# --------------------------------------------------

@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def update_epk_images(request, kit_id):
    kit = get_object_or_404(PressKit, pk=kit_id)

    if request.method == "POST":
        form = PressImageSelectionForm(request.POST, kit=kit)

        if form.is_valid():
            selected_images = form.cleaned_data["press_images"]

            # M2M path:
            if hasattr(kit.press_images, "set"):
                kit.press_images.set(selected_images)
            else:
                # FK path: attach selected, delete the rest from this kit
                selected_ids = set(selected_images.values_list("pk", flat=True))
                PressImage.objects.filter(pk__in=selected_ids).update(kit=kit)
                kit.press_images.exclude(pk__in=selected_ids).delete()

            AuditLog.objects.create(
                actor=request.user,
                action="update",
                app_label="epk",
                model_name="PressKit",
                object_id=str(kit.pk),
                object_repr=str(kit),
                changes={"selected_press_images": [p.pk for p in selected_images]},
            )

            count = (
                selected_images.count()
                if hasattr(selected_images, "count")
                else len(selected_images)
            )
            messages.success(
                request,
                f"Visibility saved — {count} image(s) will appear in the public EPK.",
            )
        else:
            for field, errors in form.errors.items():
                for err in errors:
                    messages.error(request, f"{field}: {err}")

    return redirect("epk:manage", kit_id=kit.pk)


# --------------------------------------------------
# REMOVE / EDIT / DELETE IMAGE
# --------------------------------------------------

@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def remove_epk_image(request, kit_id, image_id):
    kit = get_object_or_404(PressKit, pk=kit_id)
    photo = get_object_or_404(PressImage, pk=image_id)

    if request.method == "POST":
        if hasattr(kit.press_images, "remove"):
            kit.press_images.remove(photo)
            note = "The image has been removed from this EPK. The original file is still stored."
        else:
            # FK path: cannot detach; delete outright
            photo.delete()
            note = "The image has been deleted from this EPK and storage."

        AuditLog.objects.create(
            actor=request.user,
            action="update",
            app_label="epk",
            model_name="PressKit",
            object_id=str(kit.pk),
            object_repr=str(kit),
            changes={"removed_press_image": photo.title},
        )

        messages.success(request, note)

    return redirect("epk:manage", kit_id=kit.pk)


@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def edit_press_image(request, kit_id, image_id):
    kit = get_object_or_404(PressKit, pk=kit_id)
    photo = get_object_or_404(PressImage, pk=image_id)

    if request.method != "POST":
        return redirect("epk:manage", kit_id=kit.pk)

    form = PressImageEditForm(
        request.POST, request.FILES or None, instance=photo,
    )

    if form.is_valid():
        with transaction.atomic():
            photo = form.save()

            AuditLog.objects.create(
                actor=request.user,
                action="update",
                app_label="epk",
                model_name="PressImage",
                object_id=str(photo.pk),
                object_repr=str(photo),
                changes={
                    "title": photo.title,
                    "photographer_credit": photo.photographer_credit,
                },
            )
        messages.success(request, "Press image updated.")
    else:
        messages.error(request, "Could not update the press image.")

    return redirect("epk:manage", kit_id=kit.pk)


@login_required
@user_passes_test(is_management_user, login_url="dashboard:login")
def delete_press_image(request, kit_id, image_id):
    photo = get_object_or_404(PressImage, pk=image_id)

    if request.method == "POST":
        title, pk = photo.title, photo.pk

        with transaction.atomic():
            photo.image.delete(save=False)
            photo.delete()

            AuditLog.objects.create(
                actor=request.user,
                action="delete",
                app_label="epk",
                model_name="PressImage",
                object_id=str(pk),
                object_repr=title,
                changes={"deleted_press_image": title},
            )

        messages.success(request, f'Press image "{title}" has been deleted from storage.')

    return redirect("epk:manage", kit_id=kit_id)


# --------------------------------------------------
# GATED DOWNLOADS (new — for kit users)
# --------------------------------------------------

from pathlib import Path
from django.http import FileResponse, Http404
from apps.download.utils import log_download


@login_required
def rider_download(request, kit_id, which):
    if not request.user.can_download:
        messages.error(request, "Please verify your email address to download.")
        return redirect("account_email_verification_sent")

    kit = get_object_or_404(PressKit, pk=kit_id, is_published=True)

    lookup = {
        "technical": (kit.technical_rider, "Technical Rider"),
        "hospitality": (kit.hospitality_rider, "Hospitality Rider"),
        "stage_plot": (kit.stage_plot, "Stage Plot"),
    }
    if which not in lookup:
        raise Http404
    file_field, label = lookup[which]
    if not file_field:
        raise Http404

    log_download(
        request.user,
        title=f"{kit.title} — {label}",
        kind="epk",
        reference_id=kit.pk,
        file_url=file_field.url,
        request=request,
    )

    return FileResponse(
        file_field.open("rb"),
        as_attachment=True,
        filename=Path(file_field.name).name,
    )


@login_required
def press_image_download(request, kit_id, image_id):
    if not request.user.can_download:
        messages.error(request, "Please verify your email address to download.")
        return redirect("account_email_verification_sent")

    kit = get_object_or_404(PressKit, pk=kit_id, is_published=True)
    photo = get_object_or_404(PressImage, pk=image_id)

    if hasattr(kit.press_images, "filter"):
        if not kit.press_images.filter(pk=photo.pk).exists():
            raise Http404

    log_download(
        request.user,
        title=f"{kit.title} — {photo.title or 'Press Image'}",
        kind="epk",
        reference_id=kit.pk,
        file_url=photo.image.url,
        request=request,
    )

    return FileResponse(
        photo.image.open("rb"),
        as_attachment=True,
        filename=Path(photo.image.name).name,
    )