from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import localtime

from .forms import EventForm
from .models import Event


def event_list(request):
    events = Event.objects.filter(
        is_published=True,
        start_at__gte=timezone.now(),
    ).order_by("start_at")

    context = {
        "events_with_posters": events.exclude(
            poster=""
        ).exclude(
            poster__isnull=True
        ),
        "events_without_posters": events.filter(
            poster=""
        ) | events.filter(
            poster__isnull=True
        ),
    }

    return render(request, "events/list.html", context)


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)
    return render(request, "events/detail.html", {"event": event})


def event_calendar(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)
    start = localtime(event.start_at).strftime("%Y%m%dT%H%M%S")
    end = localtime(
        event.end_at or (event.start_at + timedelta(hours=2))
    ).strftime("%Y%m%dT%H%M%S")
    description = (event.description or "DJ ARTIST live event").replace("\n", "\\n")
    location = f"{event.venue}, {event.city_country}".strip(", ")
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//DJ Artist//Events//EN\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:event-{event.pk}@djartist\r\n"
        f"DTSTAMP:{localtime().strftime('%Y%m%dT%H%M%S')}\r\n"
        f"DTSTART:{start}\r\n"
        f"DTEND:{end}\r\n"
        f"SUMMARY:{event.title}\r\n"
        f"DESCRIPTION:{description}\r\n"
        f"LOCATION:{location}\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    response = HttpResponse(ics, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{event.slug}.ics"'
    return response


# ============================================================
# EVENT MANAGEMENT (staff only)
# ============================================================

@staff_member_required
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.title}" created.')
            return redirect("events:detail", slug=event.slug)
    else:
        form = EventForm()

    return render(
        request,
        "events/form.html",
        {
            "form": form,
            "page_title": "Add Event",
            "submit_label": "CREATE EVENT",
        },
    )


@staff_member_required
def event_update(request, slug):
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.title}" updated.')
            return redirect("events:detail", slug=event.slug)
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "events/form.html",
        {
            "form": form,
            "event": event,
            "page_title": "Edit Event",
            "submit_label": "SAVE CHANGES",
        },
    )


@staff_member_required
def event_delete(request, slug):
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect("events:list")

    return render(
        request,
        "events/confirm_delete.html",
        {"event": event},
    )