from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from datetime import datetime, time
from django.conf import settings
from django.db.models import Q

from .models import AuditLog
from django.contrib.auth import get_user_model
from qms_app.decorators import require_page_permission


@login_required
@require_page_permission("can_audit")
def audit_list(request):

    User = get_user_model()

    logs = AuditLog.objects.select_related("user").order_by("-timestamp")
    users = User.objects.all()

    selected_date = request.GET.get("date")
    selected_user = request.GET.get("user")
    selected_module = request.GET.get("module")

    # -----------------------
    # Date Filter
    # -----------------------
    if selected_date:
        parsed_date = parse_date(selected_date)

        if parsed_date:
            if settings.USE_TZ:
                start = make_aware(datetime.combine(parsed_date, time.min))
                end = make_aware(datetime.combine(parsed_date, time.max))
            else:
                start = datetime.combine(parsed_date, time.min)
                end = datetime.combine(parsed_date, time.max)

            logs = logs.filter(timestamp__range=(start, end))

    # -----------------------
    # User Filter
    # -----------------------
    if selected_user:
        logs = logs.filter(user_id=selected_user)

    # -----------------------
    # Module Filter
    # -----------------------
    if selected_module:
        logs = logs.filter(module=selected_module)

    return render(request, "audit_log/list.html", {
        "logs": logs[:500],
        "users": users,
        "selected_date": selected_date,
        "selected_user": selected_user,
        "selected_module": selected_module,
    })