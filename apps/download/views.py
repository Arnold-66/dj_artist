from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render


@login_required
def download_history(request):
    # Only kit users see this page (operators/admins have their own dashboards)
    if not getattr(request.user, "is_kit_user", False):
        return render(request, "downloads/not_allowed.html", status=403)

    logs = request.user.download_logs.select_related()
    paginator = Paginator(logs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "downloads/history.html", {"page": page})