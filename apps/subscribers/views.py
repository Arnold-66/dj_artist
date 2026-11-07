from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import SubscribeForm
from .models import Subscriber

def subscribe(request):
    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscriber, created = Subscriber.objects.update_or_create(
                email=form.cleaned_data["email"],
                defaults={
                    "name": form.cleaned_data["name"],
                    "events_opt_in": form.cleaned_data["events_opt_in"],
                    "mixes_opt_in": form.cleaned_data["mixes_opt_in"],
                    "is_confirmed": False,
                },
            )
            confirm_url = request.build_absolute_uri(reverse("subscribers:confirm", args=[subscriber.token]))
            send_mail("Confirm your DJ Artist updates", f"Please confirm your subscription: {confirm_url}", settings.DEFAULT_FROM_EMAIL, [subscriber.email], fail_silently=True)
            messages.success(request, "Please check your email to confirm your subscription.")
            return redirect("core:home")
    else:
        form = SubscribeForm()
    return render(request, "subscribers/form.html", {"form": form})

def confirm(request, token):
    subscriber = get_object_or_404(Subscriber, token=token)
    subscriber.is_confirmed = True
    subscriber.save(update_fields=["is_confirmed"])
    return render(request, "subscribers/confirmed.html")

def unsubscribe(request, token):
    subscriber = get_object_or_404(Subscriber, token=token)
    subscriber.delete()
    return render(request, "subscribers/unsubscribed.html")
