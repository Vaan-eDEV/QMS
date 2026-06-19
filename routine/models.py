from django.db import models
from django.conf import settings
from django.utils import timezone


# =========================================================
# ROUTINE CATEGORY
# =========================================================

class RoutineCategory(models.Model):

    category_name = models.CharField(
        max_length=200,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
       settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="routine_categories_created"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.category_name


# =========================================================
# ROUTINE MASTER
# =========================================================

class RoutineMaster(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    routine_no = models.CharField(
        max_length=50,
        unique=True
    )

    routine_name = models.CharField(
        max_length=300
    )

    category = models.ForeignKey(
        RoutineCategory,
        on_delete=models.PROTECT
    )

    department = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=250
    )

    machine_asset = models.CharField(
        max_length=250,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    photo_mandatory = models.BooleanField(
        default=False
    )

    attachment_mandatory = models.BooleanField(
        default=False
    )

    comment_mandatory_on_fail = models.BooleanField(
        default=True
    )

    ncr_required_on_fail = models.BooleanField(
        default=True
    )

    critical_routine = models.BooleanField(
        default=False
    )

    created_by = models.ForeignKey(
       settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="routines_created"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.routine_name


# =========================================================
# CHECKLIST ITEMS
# =========================================================

class RoutineChecklistItem(models.Model):

    RESPONSE_TYPES = [
        ('pass_fail', 'Pass / Fail'),
        ('yes_no', 'Yes / No'),
        ('numeric', 'Numeric'),
        ('text', 'Text'),
    ]

    routine = models.ForeignKey(
        RoutineMaster,
        on_delete=models.CASCADE,
        related_name='checklist_items'
    )

    sequence = models.PositiveIntegerField()

    question = models.CharField(
        max_length=500
    )

    response_type = models.CharField(
        max_length=30,
        choices=RESPONSE_TYPES,
        default='pass_fail'
    )

    expected_result = models.TextField(
        blank=True,
        null=True
    )
    photo_required = models.BooleanField(
        default=False
    )

    comment_required = models.BooleanField(
        default=False
    )
    is_critical = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.question


# =========================================================
# ROUTINE SCHEDULE
# =========================================================

class RoutineSchedule(models.Model):

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('yearly', 'Yearly'),
    ]

    routine = models.ForeignKey(
        RoutineMaster,
        on_delete=models.CASCADE
    )

    frequency = models.CharField(
        max_length=30,
        choices=FREQUENCY_CHOICES
    )

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True
    )

    due_time = models.TimeField()

    grace_hours = models.IntegerField(
        default=2
    )

    escalation_after_days = models.IntegerField(
        default=1
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='routine_assigned'
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='routine_reviewer'
    )

    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='routine_approver'
    )

    escalation_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='routine_escalation'
    )

    auto_create_checklist = models.BooleanField(
        default=True
    )

    auto_notification = models.BooleanField(
        default=True
    )

    auto_escalation = models.BooleanField(
        default=True
    )

    auto_close = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.routine.routine_name} - {self.frequency}"


# =========================================================
# GENERATED CHECKLIST
# =========================================================

class RoutineExecution(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('overdue', 'Overdue'),
        ('closed', 'Closed'),
    ]

    execution_no = models.CharField(
        max_length=50,
        unique=True
    )

    schedule = models.ForeignKey(
        RoutineSchedule,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    due_date = models.DateTimeField()

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True
    )
    execution_date = models.DateField(
        null=True,
        blank=True
    )

    is_generated = models.BooleanField(
        default=False
    )
    submitted_at = models.DateTimeField(
        blank=True,
        null=True
    )
    is_late = models.BooleanField(
        default=False
    )
    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.execution_no


# =========================================================
# CHECKLIST RESPONSE
# =========================================================

class RoutineResponse(models.Model):

    execution = models.ForeignKey(
        RoutineExecution,
        on_delete=models.CASCADE
    )

    checklist_item = models.ForeignKey(
        RoutineChecklistItem,
        on_delete=models.CASCADE
    )

    response = models.TextField()

    comments = models.TextField(
        blank=True,
        null=True
    )

    result = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )


# =========================================================
# ATTACHMENTS
# =========================================================

class RoutineAttachment(models.Model):

    execution = models.ForeignKey(
        RoutineExecution,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to='routine_attachments/'
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )


# =========================================================
# PHOTOS
# =========================================================

class RoutinePhoto(models.Model):

    response = models.ForeignKey(
        RoutineResponse,
        on_delete=models.CASCADE
    )

    photo = models.ImageField(
        upload_to='routine_photos/'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )


# =========================================================
# ACTIVITY HISTORY
# =========================================================

class RoutineActivity(models.Model):

    execution = models.ForeignKey(
        RoutineExecution,
        on_delete=models.CASCADE
    )

    activity = models.CharField(
        max_length=500
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    performed_at = models.DateTimeField(
        auto_now_add=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )


# =========================================================
# NCR LINK
# =========================================================

class RoutineNCR(models.Model):

    execution = models.ForeignKey(
        RoutineExecution,
        on_delete=models.CASCADE
    )

    response = models.ForeignKey(
        RoutineResponse,
        on_delete=models.CASCADE
    )

    ncr_no = models.CharField(
        max_length=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )