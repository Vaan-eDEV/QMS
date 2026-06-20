from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import ActivityLog


# =====================================
# LIST
# =====================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import ActivityLog


@login_required
def activity_log_list(request):

    if request.user.is_superuser:

        logs = ActivityLog.objects.all().order_by(
            "-date",
            "-created_at"
        )

    else:

        logs = ActivityLog.objects.filter(
            created_by=request.user
        ).order_by(
            "-date",
            "-created_at"
        )

    today = timezone.now().date()

    context = {

        "logs": logs,

        "total_logs": logs.count(),

        "today_logs": logs.filter(
            date=today
        ).count(),

        "open_logs": logs.filter(
            status="OPEN"
        ).count(),

        "closed_logs": logs.filter(
            status="CLOSED"
        ).count(),
    }

    return render(
        request,
        "activity_log/activity_log_list.html",
        context
    )



from django.http import JsonResponse
from django.shortcuts import get_object_or_404


@login_required
def activity_log_json(request, pk):

    log = get_object_or_404(
        ActivityLog,
        pk=pk
    )

    if (
        not request.user.is_superuser
        and log.created_by != request.user
    ):
        return JsonResponse(
            {"error": "Access Denied"},
            status=403
        )

    return JsonResponse({

        "id": log.id,

        "date": str(log.date),

        "shift": log.shift,

        "start_time": str(log.start_time),

        "end_time": str(log.end_time),

        "task_area": log.task_area,

        "task_description":
            log.task_description,

        "issues_observations":
            log.issues_observations or "",

        "status":
            log.status,
    })


# =====================================
# CREATE
# =====================================

@login_required
def activity_log_create(request):

    if request.method == "POST":

        ActivityLog.objects.create(
            work_order_id=request.POST.get("work_order") or None,
            date=request.POST.get("date"),
            shift=request.POST.get("shift"),
            task_description=request.POST.get("task_description"),
            task_area=request.POST.get("task_area"),
            start_time=request.POST.get("start_time"),
            end_time=request.POST.get("end_time"),
            issues_observations=request.POST.get(
                "issues_observations"
            ),
            created_by=request.user
        )

        messages.success(
            request,
            "Activity log created successfully."
        )

        return redirect("activity_log_list")

    return render(
        request,
        "activity_log/activity_log_form.html"
    )


# =====================================
# DETAIL
# =====================================

@login_required
def activity_log_detail(request, pk):

    log = get_object_or_404(
        ActivityLog,
        pk=pk
    )

    if not request.user.is_superuser:

        if log.created_by != request.user:
            return HttpResponseForbidden(
                "Access Denied"
            )

    return render(
        request,
        "activity_log/activity_log_detail.html",
        {
            "log": log
        }
    )


# =====================================
# EDIT
# =====================================
@login_required
def activity_log_edit(request, pk):

    log = get_object_or_404(
        ActivityLog,
        pk=pk
    )

    if (
        not request.user.is_superuser
        and log.created_by != request.user
    ):
        return HttpResponseForbidden(
            "Access Denied"
        )

    if request.method == "POST":

        log.date = request.POST.get("date")

        log.shift = request.POST.get("shift")

        log.start_time = request.POST.get(
            "start_time"
        )

        log.end_time = request.POST.get(
            "end_time"
        )

        log.task_area = request.POST.get(
            "task_area"
        )

        log.task_description = request.POST.get(
            "task_description"
        )

        log.issues_observations = request.POST.get(
            "issues_observations"
        )

        log.save()

        messages.success(
            request,
            "Activity Log Updated Successfully"
        )

        return redirect(
            "activity_log_list"
        )

    return render(
        request,
        "activity_log/activity_log_edit.html",
        {
            "log": log
        }
    )

# =====================================
# DELETE
# =====================================

@login_required
def activity_log_delete(request, pk):

    log = get_object_or_404(
        ActivityLog,
        pk=pk
    )

    if not request.user.is_superuser:

        if log.created_by != request.user:
            return HttpResponseForbidden(
                "Access Denied"
            )

    if request.method == "POST":

        log.delete()

        messages.success(
            request,
            "Activity log deleted successfully."
        )

        return redirect(
            "activity_log_list"
        )

    return render(
        request,
        "activity_log/activity_log_delete.html",
        {
            "log": log
        }
    )

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import ActivityLog

User = get_user_model()


@login_required
def activity_dashboard(request):

    selected_user = request.GET.get("user")

    from_date = request.GET.get("from_date")

    to_date = request.GET.get("to_date")

    if request.user.is_superuser:

        users = User.objects.all().order_by(
            "email"
        )

        logs = ActivityLog.objects.all()

        if selected_user:

            logs = logs.filter(
                created_by_id=selected_user
            )

    else:

        users = None

        logs = ActivityLog.objects.filter(
            created_by=request.user
        )

    # DATE FILTERS

    if from_date:

        logs = logs.filter(
            date__gte=from_date
        )

    if to_date:

        logs = logs.filter(
            date__lte=to_date
        )

    logs = logs.order_by(
        "-date",
        "-created_at"
    )

    today = timezone.now().date()

    context = {

        "users": users,

        "selected_user": selected_user,

        "from_date": from_date,

        "to_date": to_date,

        "logs": logs,

        "total_logs": logs.count(),

        "today_logs": logs.filter(
            date=today
        ).count(),

        "open_logs": logs.filter(
            status="OPEN"
        ).count(),

        "closed_logs": logs.filter(
            status="CLOSED"
        ).count(),

    }

    return render(
        request,
        "activity_log/activity_log_dashboard.html",
        context
    )