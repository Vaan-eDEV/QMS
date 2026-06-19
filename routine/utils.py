from datetime import datetime, timedelta
from django.utils import timezone
from .models import RoutineExecution
def generate_next_execution(schedule):

    last_execution = (
        RoutineExecution.objects
        .filter(schedule=schedule)
        .order_by("-execution_date")
        .first()
    )

    if not last_execution:
        return

    if schedule.frequency == "daily":
        next_date = last_execution.execution_date + timedelta(days=1)

    elif schedule.frequency == "weekly":
        next_date = last_execution.execution_date + timedelta(days=7)

    elif schedule.frequency == "monthly":
        next_date = last_execution.execution_date + timedelta(days=30)

    elif schedule.frequency == "quarterly":
        next_date = last_execution.execution_date + timedelta(days=90)

    elif schedule.frequency == "half_yearly":
        next_date = last_execution.execution_date + timedelta(days=180)

    elif schedule.frequency == "yearly":
        next_date = last_execution.execution_date + timedelta(days=365)

    else:
        return
    # ====================================
    # STOP AFTER END DATE
    # ====================================

    if schedule.end_date:

        if next_date > schedule.end_date:

            return

    # ====================================
    # PREVENT DUPLICATE EXECUTION
    # ====================================
    if RoutineExecution.objects.filter(
        schedule=schedule,
        execution_date=next_date
    ).exists():
        return

    due_datetime = timezone.make_aware(
        datetime.combine(
            next_date,
            schedule.due_time
        )
    )

    RoutineExecution.objects.create(

        execution_no=
        f"EXE-{timezone.now().strftime('%Y%m%d%H%M%S')}",

        schedule=schedule,

        execution_date=next_date,

        due_date=due_datetime,

        assigned_to=schedule.assigned_to,

        status="pending",

        is_generated=True

    )