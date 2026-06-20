from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

from qms_app.models import WorkOrder

class ActivityLog(models.Model):

    SHIFT_CHOICES = [
        ("DAY", "Day Shift"),
        ("NIGHT", "Night Shift"),
        ("GENERAL", "General"),
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    ]

    # =====================================
    # TRACEABILITY
    # =====================================

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs"
    )

    # =====================================
    # ACTIVITY LOG DETAILS
    # =====================================

    date = models.DateField()

    shift = models.CharField(
        max_length=20,
        choices=SHIFT_CHOICES,
        default="GENERAL"
    )

    task_description = models.TextField(
        verbose_name="Task / Activity Description"
    )

    task_area = models.CharField(
        max_length=200,
        verbose_name="Area of Task Performed"
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    issues_observations = models.TextField(
        blank=True,
        null=True,
        verbose_name="Issues / Observations"
    )

    # =====================================
    # SIGNATURES
    # =====================================

    supervisor_signature = models.ImageField(
        upload_to="activity_log/signatures/",
        blank=True,
        null=True
    )

    # =====================================
    # APPROVAL
    # =====================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_activity_logs"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================
    # SYSTEM FIELDS
    # =====================================

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_activity_logs"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-date", "-start_time"]
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        if self.work_order:
            return f"{self.work_order} - {self.date}"
        return f"Activity Log - {self.date}"

    @property
    def duration_hours(self):
        """
        Optional helper for reports.
        """
        from datetime import datetime

        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)

        return round(
            (end - start).total_seconds() / 3600,
            2
        )