from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.text import slugify

from apps.bookings.models import BookingInquiry
from apps.bookings.services import send_booking_reply
from apps.events.models import Event
from apps.music.models import Mix
from apps.epk.models import PressKit, PressImage
from apps.subscribers.models import Subscriber

from .decorators import admin_required, staff_required
from .forms import (
    BookingStatusForm, BookingReplyForm,
    UserCreateForm, UserEditForm,
    MixForm, EventForm,
)

User = get_user_model()


# ---------- AUTH ----------
class StaffLoginView(LoginView):
    template_name = "dashboard/login.html"
    redirect_authenticated_user = False

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_staff or not user.is_active:
            form.add_error(None, "This account does not have management access.")
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("dashboard:overview")


def staff_logout(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have successfully signed out.")
    return redirect("account_login")


# ---------- SHARED DASHBOARD ----------
@staff_required
def overview(request):
    now = timezone.now()
    context = {
        "booking_count": BookingInquiry.objects.count(),
        "new_bookings": BookingInquiry.objects.filter(status="new").count(),
        "confirmed_bookings": BookingInquiry.objects.filter(status="confirmed").count(),
        "event_count": Event.objects.filter(is_published=True).count(),
        "upcoming_events": Event.objects.filter(is_published=True, start_at__gte=now).order_by("start_at")[:5],
        "mix_count": Mix.objects.filter(is_published=True).count(),
        "video_count": Mix.objects.filter(is_published=True, media_type="video").count(),
        "audio_count": Mix.objects.filter(is_published=True, media_type="audio").count(),
        "subscriber_count": Subscriber.objects.filter(is_confirmed=True).count(),
        "recent_bookings": BookingInquiry.objects.all()[:8],
        "staff_role": "Super Administrator" if request.user.is_superuser else request.user.get_role_display(),
        "is_admin": request.user.is_superuser or request.user.is_admin_role,
    }
    return render(request, "dashboard/overview.html", context)


# ---------- BOOKINGS ----------
@staff_required
def bookings_list(request):
    bookings = BookingInquiry.objects.all()
    selected_status = request.GET.get("status", "")
    if selected_status in dict(BookingInquiry.STATUSES):
        bookings = bookings.filter(status=selected_status)

    return render(request, "dashboard/bookings_list.html", {
        "bookings": bookings,
        "selected_status": selected_status,
        "statuses": BookingInquiry.STATUSES,
        "total_count": BookingInquiry.objects.count(),
        "new_count": BookingInquiry.objects.filter(status="new").count(),
        "confirmed_count": BookingInquiry.objects.filter(status="confirmed").count(),
    })


@staff_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(BookingInquiry, pk=booking_id)
    status_form = BookingStatusForm(instance=booking)
    reply_form = BookingReplyForm(initial={"subject": f"Re: Booking inquiry - {booking.organization}"})

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_status":
            status_form = BookingStatusForm(request.POST, instance=booking)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "Booking status updated.")
                return redirect("dashboard:booking_detail", booking_id=booking.pk)
        elif action == "send_reply":
            reply_form = BookingReplyForm(request.POST)
            if reply_form.is_valid():
                reply = send_booking_reply(
                    booking=booking, sender=request.user,
                    subject=reply_form.cleaned_data["subject"],
                    message=reply_form.cleaned_data["message"],
                )
                if reply.email_status == "sent":
                    messages.success(request, "Your reply was sent.")
                else:
                    messages.error(request, "Reply could not be sent.")
                return redirect("dashboard:booking_detail", booking_id=booking.pk)

    return render(request, "dashboard/booking_detail.html", {
        "booking": booking,
        "status_form": status_form,
        "reply_form": reply_form,
        "replies": booking.replies.select_related("sender").all(),
    })


# ---------- MUSIC ----------
@staff_required
def music_list(request):
    mixes = Mix.objects.all().order_by("-created_at")
    return render(request, "dashboard/music/list.html", {"mixes": mixes})


@staff_required
def music_create(request):
    form = MixForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Music item created.")
        return redirect("dashboard:music_list")
    return render(request, "dashboard/music/form.html", {"form": form, "title": "Add Music"})


@staff_required
def music_edit(request, pk):
    mix = get_object_or_404(Mix, pk=pk)
    form = MixForm(request.POST or None, request.FILES or None, instance=mix)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Music item updated.")
        return redirect("dashboard:music_list")
    return render(request, "dashboard/music/form.html", {"form": form, "title": f"Edit: {mix.title}"})


@staff_required
def music_delete(request, pk):
    mix = get_object_or_404(Mix, pk=pk)
    if request.method == "POST":
        mix.delete()
        messages.success(request, "Music item deleted.")
        return redirect("dashboard:music_list")
    return render(request, "dashboard/music/confirm_delete.html", {"obj": mix})


# ---------- EVENTS ----------
@staff_required
def event_list(request):
    events = Event.objects.all().order_by("-start_at")
    return render(request, "dashboard/events/list.html", {"events": events})


@staff_required
def event_create(request):
    form = EventForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        if not event.slug:
            event.slug = slugify(event.title)
        event.save()
        messages.success(request, "Event created.")
        return redirect("dashboard:event_list")
    return render(request, "dashboard/events/form.html", {"form": form, "title": "Add Event"})


@staff_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, request.FILES or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect("dashboard:event_list")
    return render(request, "dashboard/events/form.html", {"form": form, "title": f"Edit: {event.title}"})


@staff_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted.")
        return redirect("dashboard:event_list")
    return render(request, "dashboard/events/confirm_delete.html", {"obj": event})



# ---------- ADMIN-ONLY: USERS ----------
@admin_required
def user_list(request):
    users = User.objects.all().order_by("-is_superuser", "username")
    return render(request, "dashboard/users/list.html", {"users": users})


@admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "User account created successfully.")
        return redirect("dashboard:user_list")
    return render(request, "dashboard/users/form.html", {"form": form, "title": "Create User"})


@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("You cannot edit a superuser account.")
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"User '{user.username}' updated.")
        return redirect("dashboard:user_list")
    return render(request, "dashboard/users/form.html", {"form": form, "title": f"Edit {user.username}", "user_obj": user})


@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("dashboard:user_list")
    if user.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("You cannot delete a superuser account.")
    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted.")
        return redirect("dashboard:user_list")
    return render(request, "dashboard/users/confirm_delete.html", {"user_obj": user})


@admin_required
def user_toggle_active(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("dashboard:user_list")
    if user.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("You cannot modify a superuser account.")
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])
    messages.success(request, f"User '{user.username}' {'activated' if user.is_active else 'deactivated'}.")
    return redirect("dashboard:user_list")