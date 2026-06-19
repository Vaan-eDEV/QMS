from django.db import models
from django.conf import settings
from django.utils import timezone

class Instrument(models.Model):


    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DUE", "Calibration Due"),
        ("OVERDUE", "Overdue"),
        ("RETIRED", "Retired"),
    ]

    instrument_id = models.CharField(
        max_length=50,
        unique=True
    )

    name = models.CharField(
        max_length=200
    )

    category = models.CharField(
        max_length=100
    )

    manufacturer = models.CharField(
        max_length=200,
        blank=True
    )

    model_no = models.CharField(
        max_length=100,
        blank=True
    )

    serial_no = models.CharField(
        max_length=100,
        blank=True
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    purchase_date = models.DateField(
        null=True,
        blank=True
    )

    range_specification = models.CharField(
        max_length=255,
        blank=True
    )

    accuracy = models.CharField(
        max_length=255,
        blank=True
    )

    calibration_frequency_days = models.PositiveIntegerField(
        default=365
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.instrument_id} - {self.name}"

    @property
    def latest_calibration(self):
        return self.calibrations.order_by(
            "-calibration_date"
        ).first()

    @property
    def next_due(self):
        latest = self.calibrations.order_by(
            "-next_due_date"
        ).first()

        return latest.next_due_date if latest else None

    @property
    def is_overdue(self):

        if not self.next_due:
            return False

        return self.next_due < timezone.now().date()

    @property
    def days_to_due(self):

        if not self.next_due:
            return None

        return (
            self.next_due -
            timezone.now().date()
        ).days
    @property
    def calibration_status(self):

        if self.is_overdue:
            return "OVERDUE"

        if (
            self.days_to_due is not None
            and self.days_to_due <= 30
        ):
            return "DUE"

        return "ACTIVE"

class CalibrationRecord(models.Model):


    RESULT_CHOICES = [
        ("PASS", "Pass"),
        ("FAIL", "Fail"),
    ]

    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name="calibrations"
    )

    calibration_date = models.DateField()

    next_due_date = models.DateField()

    certificate_number = models.CharField(
        max_length=100
    )

    calibration_agency = models.CharField(
        max_length=255
    )

    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    certificate_file = models.FileField(
        upload_to="calibration/",
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-calibration_date"]

    def __str__(self):
        return (
            f"{self.instrument.instrument_id} - "
            f"{self.calibration_date}"
        )



class MSAStudy(models.Model):

    STUDY_TYPES = [
        ("GRR", "Gauge R&R"),
        ("BIAS", "Bias"),
        ("LINEARITY", "Linearity"),
        ("STABILITY", "Stability"),
    ]

    msa_no = models.CharField(
        max_length=50,
        unique=True
    )

    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.PROTECT
    )

    study_type = models.CharField(
        max_length=20,
        choices=STUDY_TYPES
    )

    study_date = models.DateField()

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    part_number = models.CharField(
        max_length=100,
        blank=True
    )

    operator_count = models.PositiveIntegerField(
        default=3
    )

    part_count = models.PositiveIntegerField(
        default=10
    )

    trial_count = models.PositiveIntegerField(
        default=3
    )

    grr_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        ("ACCEPTED", "Accepted"),

        ("CONDITIONAL", "Conditional"),

        ("REJECTED", "Rejected"),
    ]

    study_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    def __str__(self):
        return self.msa_no


class MSAReading(models.Model):

    study = models.ForeignKey(
        MSAStudy,
        related_name="readings",
        on_delete=models.CASCADE
    )

    operator = models.CharField(
        max_length=100
    )

    part_no = models.CharField(
        max_length=100
    )

    trial_no = models.IntegerField()

    measured_value = models.DecimalField(
        max_digits=12,
        decimal_places=4
    )

    def __str__(self):
        return (
            f"{self.operator} - "
            f"{self.part_no}"
        )