from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .utils import generate_next_execution
from .models import *
import base64
from django.db.models import Q
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

User = get_user_model()

# ===================================================================
# ============================ Routine ==============================
# ===================================================================



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q

from .models import *



@login_required
def routine_dashboard(request):

    # =====================================================
    # AUTO UPDATE OVERDUE EXECUTIONS
    # =====================================================

    RoutineExecution.objects.filter(

        status__in=[
            "pending",
            "in_progress"
        ],

        due_date__lt=timezone.now()

    ).update(

        status="overdue"

    )

    # =====================================================
    # KPI COUNTS
    # =====================================================

    total_routines = RoutineMaster.objects.count()

    total_schedules = RoutineSchedule.objects.count()

    total_checklists = RoutineExecution.objects.count()

    completed = RoutineExecution.objects.filter(
        status="approved"
    ).count()

    pending = RoutineExecution.objects.filter(
        status="pending"
    ).count()

    in_progress = RoutineExecution.objects.filter(
        status="in_progress"
    ).count()

    submitted = RoutineExecution.objects.filter(
        status="submitted"
    ).count()

    reviewed = RoutineExecution.objects.filter(
        status="reviewed"
    ).count()

    overdue = RoutineExecution.objects.filter(
        status="overdue"
    ).count()

    # =====================================================
    # ROUTINE COUNTS
    # =====================================================

    scheduled_routines = RoutineMaster.objects.filter(
        routineschedule__isnull=False
    ).distinct().count()

    unscheduled_routines = RoutineMaster.objects.filter(
        routineschedule__isnull=True
    ).count()

    # =====================================================
    # COMPLETION RATE
    # =====================================================

    completion_rate = 0

    if total_checklists > 0:

        completion_rate = round(

            (
                completed
                /
                total_checklists
            ) * 100,

            2

        )

    # =====================================================
    # ACTIVE ROUTINES
    # =====================================================

    routines = RoutineMaster.objects.select_related(
        "category"
    ).prefetch_related(
        "routineschedule_set"
    ).filter(
        status="active"
    ).order_by(
        "routine_name"
    )

    # =====================================================
    # ACTIVE CATEGORIES
    # =====================================================

    categories = RoutineCategory.objects.filter(
        is_active=True
    ).order_by(
        "category_name"
    )

    # =====================================================
    # PENDING CHECKLISTS
    # =====================================================

    my_checklists = RoutineExecution.objects.select_related(

        "schedule",

        "schedule__routine",

        "assigned_to"

    ).filter(

        status__in=[

            "pending",

            "in_progress",

            "overdue"

        ]

    ).order_by(

        "due_date"

    )[:10]

    # =====================================================
    # TODAY DUE
    # =====================================================

    today_due = RoutineExecution.objects.filter(

        due_date__date=timezone.now().date(),

        status__in=[
            "pending",
            "in_progress"
        ]

    ).count()

    # =====================================================
    # RECENT CHECKLIST RECORDS
    # =====================================================

    recent_records = RoutineResponse.objects.select_related(

        "execution",

        "submitted_by",

        "checklist_item",

        "checklist_item__routine"

    ).prefetch_related(

        "routinephoto_set"

    ).order_by(

        "-submitted_at"

    )[:10]

    # =====================================================
    # RECENT ACTIVITIES
    # =====================================================

    recent_activities = RoutineActivity.objects.select_related(

        "performed_by"

    ).order_by(

        "-performed_at"

    )[:10]

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        # KPI

        "total_routines": total_routines,

        "total_schedules": total_schedules,

        "total_checklists": total_checklists,

        "completed": completed,

        "pending": pending,

        "in_progress": in_progress,

        "submitted": submitted,

        "reviewed": reviewed,

        "overdue": overdue,

        "scheduled_routines": scheduled_routines,

        "unscheduled_routines": unscheduled_routines,

        "today_due": today_due,

        "completion_rate": completion_rate,

        # Masters

        "routines": routines,

        "categories": categories,

        # Dashboard Tables

        "my_checklists": my_checklists,

        "recent_records": recent_records,

        "recent_activities": recent_activities,

    }

    return render(

        request,

        "routine/routine_dashboard.html",

        context

    )


from django.utils import timezone

def update_overdue():

    RoutineExecution.objects.filter(

        status="pending",

        due_date__lt=timezone.now()

    ).update(

        status="overdue"

    )

# ========================================================================
# ============================ Create Category ===========================
# ========================================================================

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import RoutineCategory


@login_required
def create_category(request):

    if request.method == "POST":

        category_name = request.POST.get(
            "category_name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        is_active = request.POST.get(
            "is_active"
        ) == "on"

        # ==========================
        # VALIDATION
        # ==========================

        if not category_name:

            messages.error(
                request,
                "Category Name is required."
            )

            return render(
                request,
                "routine/category_form.html"
            )

        # ==========================
        # DUPLICATE CHECK
        # ==========================

        exists = RoutineCategory.objects.filter(
            category_name__iexact=category_name
        ).exists()

        if exists:

            messages.error(
                request,
                f'"{category_name}" category already exists.'
            )

            return render(
                request,
                "routine/category_form.html"
            )

        # ==========================
        # CREATE CATEGORY
        # ==========================

        RoutineCategory.objects.create(
            category_name=category_name,
            description=description,
            is_active=is_active,
            created_by=request.user
        )

        messages.success(
            request,
            "Category created successfully."
        )

        return redirect(
            "routine:category_list"
        )

    return render(
        request,
        "routine/category_form.html"
    )

@login_required
def routine_category_list(request):

    categories = RoutineCategory.objects.all().order_by(
        "category_name"
    )

    return render(
        request,
        "routine/routine_category_list.html",
        {
            "categories": categories
        }
    )



# ================================================================
# ========================= Create Routine ========================
# ================================================================

@login_required
def create_routine(request):

    categories = RoutineCategory.objects.filter(
        is_active=True
    ).order_by(
        "category_name"
    )

    if request.method == "POST":

        try:

            routine_no = request.POST.get(
                "routine_no",
                ""
            ).strip()

            routine_name = request.POST.get(
                "routine_name",
                ""
            ).strip()

            category_id = request.POST.get(
                "category"
            )

            department = request.POST.get(
                "department",
                ""
            ).strip()

            location = request.POST.get(
                "location",
                ""
            ).strip()

            machine_asset = request.POST.get(
                "machine_asset",
                ""
            ).strip()

            description = request.POST.get(
                "description",
                ""
            ).strip()

            status = request.POST.get(
                "status",
                "active"
            )

            photo_mandatory = (
                request.POST.get(
                    "photo_mandatory"
                ) == "on"
            )

            attachment_mandatory = (
                request.POST.get(
                    "attachment_mandatory"
                ) == "on"
            )

            comment_mandatory_on_fail = (
                request.POST.get(
                    "comment_mandatory_on_fail"
                ) == "on"
            )

            ncr_required_on_fail = (
                request.POST.get(
                    "ncr_required_on_fail"
                ) == "on"
            )

            critical_routine = (
                request.POST.get(
                    "critical_routine"
                ) == "on"
            )

            # ===================================
            # VALIDATION
            # ===================================

            if not routine_no:

                messages.error(
                    request,
                    "Routine Number is required."
                )

                return redirect(
                    "routine:create_routine"
                )

            if not routine_name:

                messages.error(
                    request,
                    "Routine Name is required."
                )

                return redirect(
                    "routine:create_routine"
                )

            if not category_id:

                messages.error(
                    request,
                    "Please select a category."
                )

                return redirect(
                    "routine:create_routine"
                )

            if RoutineMaster.objects.filter(
                routine_no__iexact=routine_no
            ).exists():

                messages.error(
                    request,
                    "Routine Number already exists."
                )

                return redirect(
                    "routine:create_routine"
                )

            category = get_object_or_404(
                RoutineCategory,
                id=category_id
            )

            # ===================================
            # CREATE ROUTINE MASTER
            # ===================================

            routine = RoutineMaster.objects.create(

                routine_no=routine_no,

                routine_name=routine_name,

                category=category,

                department=department,

                location=location,

                machine_asset=machine_asset,

                description=description,

                status=status,

                photo_mandatory=photo_mandatory,

                attachment_mandatory=attachment_mandatory,

                comment_mandatory_on_fail=comment_mandatory_on_fail,

                ncr_required_on_fail=ncr_required_on_fail,

                critical_routine=critical_routine,

                created_by=request.user

            )

            # ===================================
            # SAVE CHECKLIST QUESTIONS
            # ===================================

            questions = request.POST.getlist(
                "question[]"
            )

            response_types = request.POST.getlist(
                "response_type[]"
            )

            photo_required = request.POST.getlist(
                "photo_required[]"
            )

            critical_questions = request.POST.getlist(
                "critical[]"
            )

            for index, question in enumerate(
                questions
            ):

                if question.strip():

                    RoutineChecklistItem.objects.create(

                        routine=routine,

                        sequence=index + 1,

                        question=question.strip(),

                        response_type=response_types[index],

                        photo_required=(
                            str(index)
                            in photo_required
                        ),

                        is_critical=(
                            str(index)
                            in critical_questions
                        )

                    )

            messages.success(
                request,
                "Routine and Checklist created successfully."
            )

            messages.success(
                request,
                "Routine created successfully. Please schedule the routine."
            )

            return redirect(
                "routine:routine_list"
            )

        except Exception as e:

            messages.error(
                request,
                str(e)
            )

    return render(
        request,
        "routine/create_routine.html",
        {
            "categories": categories
        }
    )




from datetime import datetime
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import (
    get_object_or_404,
    redirect
)
from django.utils import timezone


@login_required
def schedule_routine(
    request,
    routine_id
):

    routine = get_object_or_404(
        RoutineMaster,
        id=routine_id
    )

    existing_schedule = RoutineSchedule.objects.filter(
        routine=routine
    ).first()

    if request.method == "POST":

        # ====================================
        # PREVENT DUPLICATE SCHEDULE
        # ====================================

        if existing_schedule:

            messages.error(
                request,
                "This routine is already scheduled."
            )

            return redirect(
                "routine:routine_list"
            )

        try:

            # ====================================
            # CONVERT DATE & TIME
            # ====================================

            start_date = datetime.strptime(
                request.POST.get(
                    "start_date"
                ),
                "%Y-%m-%d"
            ).date()

            due_time = datetime.strptime(
                request.POST.get(
                    "due_time"
                ),
                "%H:%M"
            ).time()

            end_date = request.POST.get(
                "end_date"
            )

            if end_date:

                end_date = datetime.strptime(
                    end_date,
                    "%Y-%m-%d"
                ).date()

            else:

                end_date = None

            # ====================================
            # CREATE SCHEDULE
            # ====================================

            schedule = RoutineSchedule.objects.create(

                routine=routine,

                frequency=request.POST.get(
                    "frequency"
                ),

                start_date=start_date,

                end_date=end_date,

                due_time=due_time,

                assigned_to_id=request.POST.get(
                    "assigned_to"
                ),

                reviewer_id=request.POST.get(
                    "reviewer"
                ),

                approver_id=request.POST.get(
                    "approver"
                ),

                escalation_user_id=request.POST.get(
                    "escalation_user"
                )

            )

            # ====================================
            # CREATE FIRST EXECUTION
            # ====================================

            execution_date = start_date

            due_datetime = datetime.combine(
                execution_date,
                due_time
            )

            execution = RoutineExecution.objects.create(

                execution_no=
                f"EXE-{timezone.now().strftime('%Y%m%d%H%M%S')}",

                schedule=schedule,

                execution_date=execution_date,

                due_date=due_datetime,

                assigned_to=schedule.assigned_to,

                status="pending",

                is_generated=True

            )

            # ====================================
            # ACTIVITY LOG
            # ====================================

            RoutineActivity.objects.create(

                execution=execution,

                activity=
                f"Routine Scheduled - "
                f"{routine.routine_name}",

                performed_by=request.user,

                remarks=
                f"Schedule Created : "
                f"{execution.execution_no}"

            )

            messages.success(
                request,
                "Routine scheduled successfully."
            )

            return redirect(
                "routine:routine_list"
            )

        except Exception as e:

            messages.error(
                request,
                f"Schedule Error: {str(e)}"
            )

            return redirect(
                "routine:routine_list"
            )

    return redirect(
        "routine:routine_list"
    )
   
# ================================================================
# ======================== Routine List ===========================
# ================================================================

from django.contrib.auth import get_user_model

@login_required
def routine_list(request):

    User = get_user_model()

    routines = RoutineMaster.objects.select_related(
        "category"
    ).prefetch_related(
        "routineschedule_set"
    ).order_by(
        "-id"
    )

    users = User.objects.all()

    return render(
        request,
        "routine/routine_list.html",
        {
            "routines": routines,
            "users": users,
        }
    )

# @login_required
# def checklist_item_list(
#     request,
#     routine_id
# ):

#     routine = get_object_or_404(
#         RoutineMaster,
#         id=routine_id
#     )

#     checklist_items = RoutineChecklistItem.objects.filter(
#         routine=routine
#     ).order_by(
#         "sequence"
#     )

#     return render(
#         request,
#         "routine/checklist_item_list.html",
#         {
#             "routine": routine,
#             "checklist_items": checklist_items
#         }
#     )

@login_required
def create_checklist_item(
    request,
    routine_id
):

    routine = get_object_or_404(
        RoutineMaster,
        id=routine_id
    )

    if request.method == "POST":

        RoutineChecklistItem.objects.create(

            routine=routine,

            sequence=request.POST.get(
                "sequence"
            ),

            question=request.POST.get(
                "question"
            ),

            response_type=request.POST.get(
                "response_type"
            ),

            expected_result=request.POST.get(
                "expected_result"
            ),

            is_critical=(
                request.POST.get(
                    "is_critical"
                ) == "on"
            )

        )

        messages.success(
            request,
            "Checklist item created successfully."
        )

        return redirect(
            "routine:checklist_item_list",
            routine.id
        )

    return render(
        request,
        "routine/create_checklist_item.html",
        {
            "routine": routine
        }
    )

@login_required
def edit_checklist_item(
    request,
    item_id
):

    item = get_object_or_404(
        RoutineChecklistItem,
        id=item_id
    )

    if request.method == "POST":

        item.sequence = request.POST.get(
            "sequence"
        )

        item.question = request.POST.get(
            "question"
        )

        item.response_type = request.POST.get(
            "response_type"
        )

        item.expected_result = request.POST.get(
            "expected_result"
        )

        item.is_critical = (
            request.POST.get(
                "is_critical"
            ) == "on"
        )

        item.save()

        messages.success(
            request,
            "Checklist item updated successfully."
        )

        return redirect(
            "routine:checklist_item_list",
            item.routine.id
        )

    return render(
        request,
        "routine/edit_checklist_item.html",
        {
            "item": item
        }
    )

@login_required
def delete_checklist_item(
    request,
    item_id
):

    item = get_object_or_404(
        RoutineChecklistItem,
        id=item_id
    )

    routine_id = item.routine.id

    item.delete()

    messages.success(
        request,
        "Checklist item deleted successfully."
    )

    return redirect(
        "routine:checklist_item_list",
        routine_id
    )


@login_required
def checklist_item_list(
    request,
    routine_id
):

    routine = get_object_or_404(
        RoutineMaster,
        id=routine_id
    )

    checklist_items = RoutineChecklistItem.objects.filter(
        routine=routine
    ).order_by(
        "sequence"
    )

    schedule = RoutineSchedule.objects.filter(
        routine=routine
    ).first()

    if request.method == "POST":

        # =====================================
        # VALIDATE SCHEDULE
        # =====================================

        if not schedule:

            messages.error(
                request,
                "This routine has not been scheduled."
            )

            return redirect(
                "routine:routine_list"
            )

        # =====================================
        # GET TODAY'S EXECUTION
        # =====================================

        today = timezone.localdate()

        execution = RoutineExecution.objects.filter(

            schedule=schedule,

            execution_date=today,

            status__in=[
                "pending",
                "in_progress",
                "overdue"
            ]

        ).first()

        if not execution:

            messages.error(

                request,

                "No pending checklist found for this routine."

            )

            return redirect(
                 "routine:dashboard"
            )

        
        # =====================================
        # SAVE RESPONSES
        # =====================================

        for item in checklist_items:

            response_value = request.POST.get(
                f"response_{item.id}",
                ""
            )

            comments = request.POST.get(
                f"comment_{item.id}",
                ""
            )

            response = RoutineResponse.objects.create(

                execution=execution,

                checklist_item=item,

                response=response_value,

                comments=comments,

                submitted_by=request.user,

                result=response_value

            )

            # =====================================
            # SAVE PHOTO
            # =====================================

            photo_data = request.POST.get(
                f"photo_data_{item.id}"
            )

            if photo_data:

                try:

                    format, imgstr = photo_data.split(
                        ";base64,"
                    )

                    ext = format.split("/")[-1]

                    photo_file = ContentFile(

                        base64.b64decode(
                            imgstr
                        ),

                        name=
                        f"routine_"
                        f"{execution.id}_"
                        f"{item.id}."
                        f"{ext}"

                    )

                    RoutinePhoto.objects.create(

                        response=response,

                        photo=photo_file

                    )

                except Exception as e:

                    print(
                        "Photo Save Error:",
                        e
                    )

            # =====================================
            # NCR CREATION
            # =====================================

            if (

                response_value.lower() in [
                    "fail",
                    "no"
                ]

                and

                routine.ncr_required_on_fail

            ):

                RoutineNCR.objects.create(

                    execution=execution,

                    response=response,

                    ncr_no=
                    f"NCR-{timezone.now().strftime('%Y%m%d%H%M%S')}",

                    created_by=request.user

                )

        # =====================================
        # ACTIVITY LOG
        # =====================================

        RoutineActivity.objects.create(

            execution=execution,

            activity=
            f"Checklist submitted for "
            f"{routine.routine_name}",

            performed_by=request.user,

            remarks=
            f"Execution No: "
            f"{execution.execution_no}"

        )
        # =====================================
        # UPDATE EXECUTION
        # =====================================

        execution.submitted_at = timezone.now()

        if execution.submitted_at > execution.due_date:

            execution.is_late = True

        execution.status = "submitted"

        execution.save()

        generate_next_execution(schedule)

        messages.success(
            request,
            "Checklist submitted successfully."
        )
        return redirect(
             "routine:dashboard"
        )

    return render(

        request,

        "routine/checklist_item_list.html",

        {

            "routine": routine,

            "checklist_items": checklist_items,

            "schedule": schedule,

        }

    )

@login_required
def checklist_records(request):

    # =====================================
    # GET RESPONSES
    # =====================================

    responses = RoutineResponse.objects.select_related(

        "execution",
        "checklist_item",
        "submitted_by",
        "checklist_item__routine"

    ).order_by(

        "-submitted_at"

    )

    # =====================================
    # GET FILTERS
    # =====================================

    department = request.GET.get(
        "department",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    from_date = request.GET.get(
        "from_date",
        ""
    ).strip()

    to_date = request.GET.get(
        "to_date",
        ""
    ).strip()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    # =====================================
    # SEARCH FILTER
    # =====================================

    if search:

        responses = responses.filter(

            Q(
                checklist_item__routine__routine_name__icontains=search
            )
            |
            Q(
                checklist_item__question__icontains=search
            )
            |
            Q(
                comments__icontains=search
            )

        )

    # =====================================
    # DEPARTMENT FILTER
    # =====================================

    if department:

        responses = responses.filter(

            checklist_item__routine__department__icontains=department

        )

    # =====================================
    # RESPONSE STATUS FILTER
    # =====================================

    if status:

        responses = responses.filter(

            response__iexact=status

        )

    # =====================================
    # FROM DATE FILTER
    # =====================================

    if from_date:

        responses = responses.filter(

            submitted_at__date__gte=from_date

        )

    # =====================================
    # TO DATE FILTER
    # =====================================

    if to_date:

        responses = responses.filter(

            submitted_at__date__lte=to_date

        )

    # =====================================
    # COUNTS
    # =====================================

    total_records = responses.count()

    pass_count = responses.filter(
        response__iexact="Pass"
    ).count()

    fail_count = responses.filter(
        response__iexact="Fail"
    ).count()

    yes_count = responses.filter(
        response__iexact="Yes"
    ).count()

    no_count = responses.filter(
        response__iexact="No"
    ).count()

    # =====================================
    # CONTEXT
    # =====================================

    context = {

        "responses": responses,

        "total_records": total_records,

        "pass_count": pass_count,

        "fail_count": fail_count,

        "yes_count": yes_count,

        "no_count": no_count,

        "department": department,

        "status": status,

        "from_date": from_date,

        "to_date": to_date,

        "search": search,

    }

    return render(

        request,

        "routine/checklist_records.html",

        context

    )

@login_required
def my_checklists(request):

    executions = RoutineExecution.objects.select_related(
        "schedule",
        "schedule__routine",
        "assigned_to"
    ).all()

    print(
        "TOTAL EXECUTIONS:",
        executions.count()
    )

    context = {

        "executions": executions,

        "pending_count": executions.filter(
            status="pending"
        ).count(),

        "in_progress_count": executions.filter(
            status="in_progress"
        ).count(),

        "overdue_count": executions.filter(
            status="overdue"
        ).count(),

    }

    return render(
        request,
        "routine/my_checklists.html",
        context
    )