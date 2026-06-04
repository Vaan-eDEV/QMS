from django.db import models
from django.conf import settings
from django.utils import timezone

from django.core.files import File

import uuid
import qrcode

from io import BytesIO


# =========================================================
# VISITOR
# =========================================================

class Visitor(models.Model):

    STATUS_CHOICES = [

        ("PENDING", "Pending"),

        ("APPROVED", "Approved"),

        ("CHECKED_IN", "Checked In"),

        ("CHECKED_OUT", "Checked Out"),

        ("REJECTED", "Rejected"),

    ]

    # =====================================================
    # BASIC
    # =====================================================

    visitor_id = models.CharField(

        max_length=50,

        unique=True,

        blank=True
    )

    name = models.CharField(
        max_length=255
    )

    company = models.CharField(

        max_length=255,

        blank=True,

        null=True
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField(

        blank=True,

        null=True
    )

    purpose = models.TextField(

        blank=True,

        null=True
    )

    # =====================================================
    # VISIT INFO
    # =====================================================

    host_employee = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="hosted_visitors"
    )

    department = models.CharField(

        max_length=255,

        blank=True,

        null=True
    )

    # =====================================================
    # PHOTO
    # =====================================================

    visitor_photo = models.ImageField(

        upload_to="visitor_photos/",

        blank=True,

        null=True
    )

    id_proof = models.ImageField(

        upload_to="visitor_ids/",

        blank=True,

        null=True
    )

    # =====================================================
    # VEHICLE
    # =====================================================

    vehicle_number = models.CharField(

        max_length=100,

        blank=True,

        null=True
    )

    # =====================================================
    # CHECK IN / OUT
    # =====================================================

    check_in_time = models.DateTimeField(

        blank=True,

        null=True
    )

    check_out_time = models.DateTimeField(

        blank=True,

        null=True
    )

    # =====================================================
    # STATUS
    # =====================================================

    status = models.CharField(

        max_length=30,

        choices=STATUS_CHOICES,

        default="PENDING"
    )

    # =====================================================
    # APPROVAL
    # =====================================================

    approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="approved_visitors"
    )

    security_approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="security_approved_visitors"
    )

    # =====================================================
    # QR / PASS
    # =====================================================

    qr_code = models.ImageField(

        upload_to="visitor_qr/",

        blank=True,

        null=True
    )

    badge_number = models.CharField(

        max_length=50,

        unique=True,

        blank=True,

        null=True
    )

    # =====================================================
    # AUDIT
    # =====================================================

    created_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="created_visitors"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self, *args, **kwargs):

        # =================================================
        # VISITOR ID
        # =================================================

        if not self.visitor_id:

            self.visitor_id = (

                f"VIS-"

                f"{timezone.now().strftime('%Y%m%d')}-"

                f"{str(uuid.uuid4())[:5].upper()}"

            )

        # =================================================
        # BADGE NUMBER
        # =================================================

        if not self.badge_number:

            last_id = Visitor.objects.count() + 1

            self.badge_number = (
                f"B-{str(last_id).zfill(4)}"
            )

        # =================================================
        # QR GENERATION
        # =================================================

        if not self.qr_code:

            qr_data = (

                f"Visitor ID: {self.visitor_id}\n"

                f"Name: {self.name}\n"

                f"Company: {self.company}\n"

                f"Phone: {self.phone}\n"

                f"Status: {self.status}"

            )

            qr = qrcode.make(qr_data)

            buffer = BytesIO()

            qr.save(buffer, format="PNG")

            file_name = (
                f"{self.visitor_id}.png"
            )

            self.qr_code.save(

                file_name,

                File(buffer),

                save=False

            )

        super().save(*args, **kwargs)

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (
            f"{self.visitor_id} - {self.name}"
        )


# =========================================================
# VISITOR BELONGINGS
# =========================================================

class VisitorBelonging(models.Model):

    # =====================================================
    # VISITOR LINK
    # =====================================================

    visitor = models.ForeignKey(

        Visitor,

        on_delete=models.CASCADE,

        related_name="belongings"
    )

    # =====================================================
    # AUTO BELONGING ID
    # =====================================================

    serial_id = models.CharField(

        max_length=50,

        unique=True,

        blank=True,

        null=True
    )

    # =====================================================
    # ITEM DETAILS
    # =====================================================

    item_name = models.CharField(
        max_length=255
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    serial_number = models.CharField(

        max_length=255,

        blank=True,

        null=True
    )

    remarks = models.TextField(

        blank=True,

        null=True
    )

    # =====================================================
    # RETURN TRACKING
    # =====================================================

    returned = models.BooleanField(
        default=False
    )

    returned_at = models.DateTimeField(

        blank=True,

        null=True
    )

    # =====================================================
    # AUDIT
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self, *args, **kwargs):

        # ================================================
        # AUTO SERIAL ID
        # ================================================

        if not self.serial_id:

            last_id = (
                VisitorBelonging.objects.count() + 1
            )

            self.serial_id = (
                f"BEL-{str(last_id).zfill(5)}"
            )

        super().save(*args, **kwargs)

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (

            f"{self.serial_id} - "

            f"{self.visitor.name} - "

            f"{self.item_name}"

        )