from django.db import models
from django.conf import settings
from django.utils import timezone
import statistics
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

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("CONDITIONAL", "Conditional"),
        ("REJECTED", "Rejected"),
    ]

    # ==========================
    # BASIC INFORMATION
    # ==========================

    msa_no = models.CharField(
        max_length=50,
        unique=True
    )

    study_type = models.CharField(
        max_length=20,
        choices=STUDY_TYPES
    )

    study_date = models.DateField()

    # ==========================
    # PART INFORMATION
    # ==========================

    part_name = models.CharField(
        max_length=255,
        blank=True
    )

    part_number = models.CharField(
        max_length=100,
        blank=True
    )

    # ==========================
    # EQUIPMENT INFORMATION
    # ==========================

    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.PROTECT
    )

    equipment_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    equipment_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    least_count = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )
    mean_value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )
    # ==========================
    # STUDY PARAMETERS
    # ==========================

    operator_names = models.JSONField(
        default=list,
        blank=True
    )

    part_count = models.PositiveIntegerField(
        default=10
    )

    trial_count = models.PositiveIntegerField(
        default=3
    )

    # ==========================
    # SPECIFICATION LIMITS
    # ==========================

    max_value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )

    min_value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )

    tolerance = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )

    # ==========================
    # DOCUMENT CONTROL
    # ==========================

    record_number = models.CharField(
        max_length=100,
        blank=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    # ==========================
    # RESULTS
    # ==========================

    grr_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    study_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    # Future AIAG values
    ev = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True
    )

    av = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True
    )

    pv = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True
    )

    tv = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True
    )
    rr = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True
    )
    ndc = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    percent_ev = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    percent_av = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    percent_rr = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    percent_pv = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    # ==========================
    # AUDIT
    # ==========================

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def operator_count(self):
        return len(self.operator_names or [])

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
        decimal_places=4,
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.operator} - "
            f"{self.part_no}"
        )


class MSAPart(models.Model):

    study = models.ForeignKey(
        MSAStudy,
        on_delete=models.CASCADE,
        related_name="parts"
    )

    part_no = models.CharField(
        max_length=100
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    class Meta:
        ordering = ["id"]














class SPCControlPlan(models.Model):

    plan_no = models.CharField(
        max_length=50,
        unique=True
    )

    part_number = models.CharField(
        max_length=100
    )

    characteristic = models.CharField(
        max_length=255
    )

    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.PROTECT
    )

    lsl = models.DecimalField(
        max_digits=12,
        decimal_places=4
    )

    target = models.DecimalField(
        max_digits=12,
        decimal_places=4
    )

    usl = models.DecimalField(
        max_digits=12,
        decimal_places=4
    )

    sample_size = models.PositiveIntegerField(
        default=5
    )

    frequency = models.CharField(
        max_length=100,
        default="Hourly"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.plan_no


    @property
    def average(self):

        readings = [
            float(r.measured_value)
            for r in self.readings.all()
        ]

        if not readings:
            return None

        return round(
            sum(readings) /
            len(readings),
            4
        )


    @property
    def cp(self):

        readings = [
            float(r.measured_value)
            for r in self.readings.all()
        ]

        if len(readings) < 2:
            return None

        std_dev = statistics.stdev(
            readings
        )

        if std_dev == 0:
            return None

        cp = (
            (
                float(self.usl)
                -
                float(self.lsl)
            )
            /
            (
                6 * std_dev
            )
        )

        return round(
            cp,
            2
        )


    @property
    def cpk(self):

        readings = [
            float(r.measured_value)
            for r in self.readings.all()
        ]

        if len(readings) < 2:
            return None

        avg = (
            sum(readings)
            /
            len(readings)
        )

        std_dev = statistics.stdev(
            readings
        )

        if std_dev == 0:
            return None

        cpu = (
            float(self.usl)
            -
            avg
        ) / (
            3 * std_dev
        )

        cpl = (
            avg
            -
            float(self.lsl)
        ) / (
            3 * std_dev
        )

        return round(
            min(cpu, cpl),
            2
        )

class SPCReading(models.Model):

    control_plan = models.ForeignKey(
        SPCControlPlan,
        related_name="readings",
        on_delete=models.CASCADE
    )

    sample_no = models.CharField(
        max_length=50
    )

    measured_value = models.DecimalField(
        max_digits=12,
        decimal_places=4
    )

    reading_date = models.DateTimeField(
        auto_now_add=True
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return (
            f"{self.control_plan.plan_no}"
            f" - {self.sample_no}"
        )