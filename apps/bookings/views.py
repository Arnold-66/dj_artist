from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    BookingInquiryForm,
    BookingReplyForm,
    BookingStatusForm,
)
from .models import BookingInquiry
from .services import (
    notify_new_booking,
    send_booking_confirmation,
    send_booking_reply,
)


# =====================================================================
# PUBLIC VIEW
# =====================================================================
def booking_create(request):
    if request.method == "POST":
        form = BookingInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()

            # 1) Notify the team.
            notify_new_booking(inquiry)

            # 2) Send a confirmation to the person who submitted it.
            send_booking_confirmation(inquiry)

            messages.success(
                request,
                "Thank you. Your booking inquiry has been received "
                "and a confirmation email has been sent to you.",
            )
            return redirect("bookings:create")
    else:
        form = BookingInquiryForm()

    return render(request, "bookings/form.html", {"form": form})


# =====================================================================
# STAFF VIEWS
# =====================================================================
@staff_member_required
def bookings_list(request):
    bookings = BookingInquiry.objects.all()

    selected_status = request.GET.get("status", "")
    if selected_status in dict(BookingInquiry.STATUSES):
        bookings = bookings.filter(status=selected_status)

    return render(
        request,
        "bookings/bookings_list.html",
        {
            "bookings": bookings,
            "selected_status": selected_status,
            "statuses": BookingInquiry.STATUSES,
            "total_count": BookingInquiry.objects.count(),
            "new_count": BookingInquiry.objects.filter(status="new").count(),
            "confirmed_count": BookingInquiry.objects.filter(
                status="confirmed"
            ).count(),
        },
    )


@staff_member_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(BookingInquiry, pk=booking_id)

    status_form = BookingStatusForm(instance=booking)
    reply_form = BookingReplyForm(
        initial={
            "subject": f"Re: Booking inquiry - {booking.organization}",
        }
    )

    if request.method == "POST":
        action = request.POST.get("action")

        # ---- Update status ----
        if action == "update_status":
            status_form = BookingStatusForm(request.POST, instance=booking)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "Booking status updated.")
                return redirect(
                    "bookings:booking_detail", booking_id=booking.pk
                )

        # ---- Send email reply ----
        elif action == "send_reply":
            reply_form = BookingReplyForm(request.POST)
            if reply_form.is_valid():
                reply = send_booking_reply(
                    booking=booking,
                    sender=request.user,
                    subject=reply_form.cleaned_data["subject"],
                    message=reply_form.cleaned_data["message"],
                )
                if reply.email_status == "sent":
                    messages.success(request, "Your reply was sent.")
                else:
                    messages.error(request, "Reply could not be sent.")
                return redirect(
                    "bookings:booking_detail", booking_id=booking.pk
                )

    return render(
        request,
        "bookings/booking_detail.html",
        {
            "booking": booking,
            "status_form": status_form,
            "reply_form": reply_form,
            "replies": booking.replies.select_related("sender").all(),
        },
    )