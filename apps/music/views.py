import io
from pathlib import Path

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MixForm
from .models import Mix
from apps.download.utils import log_download


def mix_list(request):
    videos = Mix.objects.filter(is_published=True, media_type="video")
    audios = Mix.objects.filter(is_published=True, media_type="audio")

    platform_order = ["Spotify", "SoundCloud", "Audiomack"]
    audio_groups = []

    for platform in platform_order:
        tracks = audios.filter(platform__iexact=platform)
        if tracks.exists():
            audio_groups.append({"name": platform, "tracks": tracks})

    other_tracks = (
        audios.exclude(platform__iexact="Spotify")
        .exclude(platform__iexact="SoundCloud")
        .exclude(platform__iexact="Audiomack")
    )
    if other_tracks.exists():
        audio_groups.append({"name": "Other Platforms", "tracks": other_tracks})

    return render(
        request,
        "music/list.html",
        
        {"videos": videos, "audio_groups": audio_groups, "total_audio_count": audios.count(),},
    )


@staff_member_required
def mix_add(request):
    if request.method == "POST":
        form = MixForm(request.POST, request.FILES)
        if form.is_valid():
            mix = form.save()
            messages.success(request, f'"{mix.title}" was added successfully.')
            return redirect("music:list")
    else:
        form = MixForm()

    return render(request, "music/add.html", {"form": form})


@staff_member_required
def mix_edit(request, pk):
    """Edit an existing video or audio mix (staff only)."""
    mix = get_object_or_404(Mix, pk=pk)

    if request.method == "POST":
        form = MixForm(request.POST, request.FILES, instance=mix)
        if form.is_valid():
            mix = form.save()
            messages.success(request, f'"{mix.title}" was updated successfully.')
            return redirect("music:list")
    else:
        form = MixForm(instance=mix)

    return render(
        request,
        "music/edit.html",
        {"form": form, "mix": mix},
    )


@staff_member_required
def mix_delete(request, pk):
    """Delete an existing video or audio mix (staff only)."""
    mix = get_object_or_404(Mix, pk=pk)

    if request.method == "POST":
        title = mix.title
        mix.delete()
        messages.success(request, f'"{title}" was deleted successfully.')
        return redirect("music:list")

    return render(
        request,
        "music/delete_confirm.html",
        {"mix": mix},
    )


# ---------------------------------------------------------------------
# DOWNLOAD — embeds cover art into MP3 ID3 tags so phones show album art
# ---------------------------------------------------------------------
@login_required
def mix_download(request, pk):
    mix = get_object_or_404(Mix, pk=pk, is_published=True)

    file_field = None
    mime_type = None
    is_audio = False

    if mix.media_type == "video" and mix.video_file:
        file_field = mix.video_file
        mime_type = "video/mp4"
    elif mix.media_type == "audio" and mix.audio_file:
        file_field = mix.audio_file
        mime_type = "audio/mpeg"
        is_audio = True

    if not file_field:
        messages.error(request, "No downloadable file is attached to this mix.")
        return redirect("music:list")

    filename = Path(file_field.name).name

    # If audio + cover image: rewrite ID3 tags with cover art.
    if is_audio and mix.cover_image:
        try:
            buffer = _embed_cover_in_audio(file_field, mix)
            if buffer:
                return FileResponse(
                    buffer,
                    as_attachment=True,
                    filename=filename,
                    content_type=mime_type,
                )
        except Exception:
            # Fall back to raw download if ID3 tagging fails
            pass

    # Default: stream raw file
    return FileResponse(
        file_field.open("rb"),
        as_attachment=True,
        filename=filename,
        content_type=mime_type or "application/octet-stream",
    )


def _embed_cover_in_audio(file_field, mix):
    """
    Read the uploaded audio, embed the cover image as ID3 APIC frame
    (album art), and return an in-memory BytesIO ready for download.
    Returns None if the format can't be tagged.
    """
    try:
        from mutagen.id3 import ID3, APIC, ID3NoHeaderError
        from mutagen.mp3 import MP3
        from mutagen import File as MutagenFile
    except ImportError:
        return None

    stream = io.BytesIO(file_field.read())
    stream.seek(0)

    # Cover image bytes + MIME
    cover_bytes = mix.cover_image.read()
    mix.cover_image.seek(0)

    cover_ext = Path(mix.cover_image.name).suffix.lower().lstrip(".")
    cover_mime = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(cover_ext, "image/jpeg")

    suffix = Path(file_field.name).suffix.lower()

    if suffix in {".mp3", ".m4a", ".mp4"}:
        # MP3 / M4A: use mutagen's ID3 tagging
        try:
            try:
                tags = ID3(stream)
            except ID3NoHeaderError:
                tags = ID3()

            tags.add(
                APIC(
                    encoding=3,
                    mime=cover_mime,
                    type=3,  # 3 = front cover
                    desc="Cover",
                    data=cover_bytes,
                )
            )
            tags.add(
                __import__("mutagen.id3", fromlist=["TIT2"]).TIT2(
                    encoding=3, text=mix.title
                )
            )
            tags.save(stream)

            stream.seek(0)
            return stream
        except Exception:
            return None

    return None



@login_required
def mix_download(request, pk):
    user = request.user

    # Gate 1: must be a verified user (or staff/operator)
    if not user.can_download:
        messages.error(
            request,
            "Please verify your email address before downloading. "
            "Check your inbox for the verification link.",
        )
        return redirect("account_email_verification_sent")  # allauth

    # Gate 2: kit users can only download audio; operators/admin can download anything
    mix = get_object_or_404(Mix, pk=pk, is_published=True)
    if user.is_kit_user and mix.media_type == "video":
        messages.error(request, "Kit users may only download audio tracks.")
        return redirect("music:list")

    file_field = None
    mime_type = None
    is_audio = False

    if mix.media_type == "video" and mix.video_file:
        file_field = mix.video_file
        mime_type = "video/mp4"
    elif mix.media_type == "audio" and mix.audio_file:
        file_field = mix.audio_file
        mime_type = "audio/mpeg"
        is_audio = True

    if not file_field:
        messages.error(request, "No downloadable file is attached to this mix.")
        return redirect("music:list")

    filename = Path(file_field.name).name

    # Log the download
    log_download(
        user,
        title=mix.title,
        kind="audio" if is_audio else "video",
        reference_id=mix.pk,
        file_url=file_field.url,
        request=request,
    )

    # (kept) embed cover art in ID3 tags for audio
    if is_audio and mix.cover_image:
        try:
            buffer = _embed_cover_in_audio(file_field, mix)
            if buffer:
                return FileResponse(
                    buffer, as_attachment=True, filename=filename, content_type=mime_type,
                )
        except Exception:
            pass

    return FileResponse(
        file_field.open("rb"),
        as_attachment=True,
        filename=filename,
        content_type=mime_type or "application/octet-stream",
    )