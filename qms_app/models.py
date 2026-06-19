from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
#from .models import QMSProcess
from django.core.validators import MaxLengthValidator
from po_qu.models import WorkOrderItem

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
# -------------------------------------------------
# QMS Stages
# -------------------------------------------------
STAGES = [
    ("rfq_po",        "Customer RFQ to PO Confirmation"),
    ("po_wo",         "From PO to Work Order"),
    ("design",        "Design Engineering"),
    ("planning",      "Planning & Material Procurement"),
    ("production",    "Production"),
    ("documentation", "Documentation & Dispatch"),
    ("post_dispatch", "Post Dispatch"),
]

# Stage → Role map
STAGE_ROLE_MAP = {
    "rfq_po":        "sales",
    "po_wo":         "sales",
    "design":        "design",
    "planning":      "planning",
    "production":    "production",
    "documentation": "documentation",
    "post_dispatch": "post",
}

# -------------------------------------------------
# Custom User Manager
# -------------------------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# -------------------------------------------------
# Custom User Model
# -------------------------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("admin",        "Admin"),
        ("student",      "Student"),
        ("user",          "User"), 

    ]

    email      = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name  = models.CharField(max_length=50, blank=True)
    role       = models.CharField(max_length=30, choices=ROLE_CHOICES, default="sales")

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)

    failed_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    password_changed_at = models.DateTimeField(default=timezone.now)

    objects    = CustomUserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    def get_display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email.split("@")[0]



class Certificate(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class CertificateCategory(models.Model):
    name = models.CharField(max_length=100)
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name="categories"
    )
    def __str__(self):
        return f"{self.name} ({self.certificate.name})"

class QMSDocument(models.Model):
    title = models.CharField(max_length=255)
    folder = models.ForeignKey(
        'DocumentFolder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents"
    )
    original_file = models.FileField(upload_to="qms_docs/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('process_owner', 'Process Owner'),
            ('reviewed', 'Reviewed'),
            ('approved', 'Approved'),
            ("completed", "Completed") 
        ],
        default='process_owner'
    )
    target_folder = models.ForeignKey(
        'DocumentFolder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="target_docs"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_documents"
    )
    

    last_message = models.TextField(blank=True, null=True)

    is_read = models.BooleanField(default=True)
    certificate = models.ManyToManyField(
        Certificate,
        blank=True, related_name="temp_fix"
    )
    certificate_category = models.ManyToManyField(
        CertificateCategory,
        blank=  True
    )
    clause = models.CharField(max_length=255,default="")
    pdf_signatures = models.JSONField(default=list, blank=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return self.title


class QMSDocumentVersion(models.Model):
    document = models.ForeignKey(QMSDocument, on_delete=models.CASCADE, related_name="versions")
    version_number = models.DecimalField(max_digits=5,decimal_places=2)
    edited_html = models.TextField()
    edited_docx = models.FileField(upload_to="qms_docs/versions/")
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"
    


class DocumentFolder(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return self.name

class DocumentRevision(models.Model):
    document = models.ForeignKey(QMSDocument, on_delete=models.CASCADE, related_name="revisions")
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    edited_at = models.DateTimeField(auto_now_add=True)
    change_summary = models.TextField(blank=True, null=True)  # can store HTML diff
    edited_html = models.TextField(blank=True, null=True)

    # Optional: store version number so you can display in revision panel
    version_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.document.title} - v{self.version_number}" 

# models.py
from django.db import models

class UploadedImage(models.Model):
    file = models.ImageField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.file.name
    

class DocumentWorkflowLog(models.Model):
    document = models.ForeignKey(QMSDocument, on_delete=models.CASCADE)
    stage = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class MaterialBatch(models.Model):

    material_name = models.CharField(max_length=200)

    supplier = models.CharField(max_length=200)

    lot_number = models.CharField(max_length=100)

    received_date = models.DateTimeField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.material_name} - {self.lot_number}"






class FormBatch(models.Model):
    form = models.ForeignKey("Form", on_delete=models.CASCADE)

    # 🔥 User-entered batch number (NO UUID now)
    batch_id = models.CharField(
        max_length=50,
        
    )

    # 🔥 Keep flow_id for internal multi-form tracking
    flow_id = models.UUIDField(
        default=uuid.uuid4,
        db_index=True
    )

    current_stage = models.ForeignKey(
        "Stage",
        on_delete=models.CASCADE,
        related_name="batches"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)


    material_batch = models.ForeignKey(
        MaterialBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    company_name = models.CharField(
        max_length=255, blank=False, null=False
    )
    origin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="origin_batches"
    )
    rfq_ref_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.batch_id} - {self.company_name}"
    class Meta:
        unique_together = ("form","company_name", "batch_id")


# models.py

class FormFolder(models.Model):
    name = models.CharField(max_length=150)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "parent")

    def __str__(self):
        if self.parent:
            return f"{self.parent} → {self.name}"
        return self.name


class Form(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    require_part_id = models.BooleanField(default=False)
    folder = models.ForeignKey(
        FormFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forms"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,related_name='qms_forms'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Stage(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)


    allowed_roles = models.JSONField(
        default=list,
        help_text="Roles allowed to fill this stage"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.form.name} - {self.name}"

    def can_be_filled_by(self, user):
        return user.is_authenticated and user.role in self.allowed_roles
    

class SubStage(models.Model):
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name="sub_stages"
    )
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("stage", "name")

    def __str__(self):
        return f"{self.stage.name} → {self.name}"





class BatchPart(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("NCR", "Under NCR"),
        ("REWORK", "Rework"),
        ("SCRAP", "Scrapped"),
    ]

    batch = models.ForeignKey(
        FormBatch,
        on_delete=models.CASCADE,
        related_name="parts"
    )

    part_id = models.CharField(max_length=100)

    current_stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name="parts"
    )

    # 🔴 QUALITY STATUS (NEW)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    # 🔁 WORKFLOW STATUS (KEEP THIS)
    is_active = models.BooleanField(default=True)
    material_batch = models.ForeignKey(
        MaterialBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    moved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moved_parts"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("batch", "part_id")

    def __str__(self):
        return f"{self.batch.batch_id} - {self.part_id}"

    # 🔍 HELPER METHODS (Professional Upgrade)

    def is_under_ncr(self):
        return self.status == "NCR"

    def can_move(self):
        return self.status == "ACTIVE"
    

class StageHistory(models.Model):
    batch = models.ForeignKey(FormBatch, on_delete=models.CASCADE)
    part = models.ForeignKey(
        BatchPart,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    from_stage = models.ForeignKey("Stage", on_delete=models.SET_NULL, null=True, related_name="+")
    to_stage = models.ForeignKey("Stage", on_delete=models.CASCADE, related_name="+")
    moved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    moved_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

class FinalProduct(models.Model):

    serial_number = models.CharField(max_length=100, unique=True)

    part = models.ForeignKey(
        BatchPart,
        on_delete=models.CASCADE,
        related_name="products"
    )

    manufactured_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return self.serial_number
# Fields inside stages
# class FormField(models.Model):
#     FIELD_TYPES = [
#         ('text', 'Text'),
#         ('textarea', 'Textarea'),
#         ('number', 'Number'),
#         ('date', 'Date'),
#         ('select', 'Select'),
#         ('checkbox', 'Checkbox'),
#     ]

#     stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='fields')
#     label = models.CharField(max_length=255)
#     field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text')
#     order = models.PositiveIntegerField(default=0)
#     options = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Comma-separated options for select/checkbox"
#     )
#     required = models.BooleanField(default=False, help_text="Is this field required?")

#     class Meta:
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.stage.name} - {self.label}"
class FormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('textarea', 'Textarea'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('select', 'Select'),
        ('checkbox', 'Checkbox'),
        ('table', 'Table / Matrix'),
        ('image_upload', 'Image Upload'),
        ('image_capture', 'Image Capture'),
    ]

    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name='fields'
    )

    sub_stage = models.ForeignKey(
        SubStage,
        on_delete=models.CASCADE,
        related_name='fields',
        null=True,
        blank=True
    )

    label = models.CharField(max_length=255)

    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPES,
        default='text'
    )

    order = models.PositiveIntegerField(default=0)

    options = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated options"
    )

    table_columns = models.JSONField(
        blank=True,
        null=True,
        help_text="Example: ['Parameter', 'As per PO', 'As per MTC', 'Accept / Reject']"
    )
    table_row_header = models.CharField(max_length=255, blank=True, null=True)

    # 🆕 ADD THIS FIELD
    table_rows = models.JSONField(
        blank=True,
        null=True,
        help_text="First column row names"
    )

    required = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.stage.name} - {self.label}"


# User submissions
class FormSubmission(models.Model):
    form = models.ForeignKey('Form', on_delete=models.CASCADE, related_name='submissions')
    stage = models.ForeignKey('Stage', on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, blank=True)
    submission_batch = models.CharField(max_length=50)
    part = models.ForeignKey(
        BatchPart,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="submissions"
    )

    def __str__(self):
        return f"{self.form.name} — {self.stage.name} by {self.submitted_by or 'Anonymous'}"

from django.db import models
from django.conf import settings


class SignatureVerification(models.Model):
    SLOT_CHOICES = [
        ("prepared", "Prepared"),
        ("approved", "Approved"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150)
    reference_code = models.CharField(max_length=20, unique=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    batch_id = models.CharField(max_length=50, db_index=True)
    slot = models.CharField(max_length=20, choices=SLOT_CHOICES)

    def __str__(self):
        return f"{self.display_name} ({self.get_slot_display()}) — {self.reference_code}"



class FormFlow(models.Model):

    name = models.CharField(max_length=255)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # store order like:
    # [ {form:1, stages:[...]}, {form:2, stages:[...]} ]
    
    structure = models.JSONField(
        default=list,      # ✅ ADD THIS
        blank=True
    )

    def __str__(self):
        return self.name

# ---------------------------------------------------------------------setting----------------------------------------------------------

class UserPageAccess(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="page_access"
    )

    # Page permissions
    can_dashboard = models.BooleanField(default=True)
    can_forms = models.BooleanField(default=True)
    can_submitted = models.BooleanField(default=False)
    can_sop = models.BooleanField(default=False)
    can_documents = models.BooleanField(default=True)
    can_userdetail = models.BooleanField(default=False)
    can_materialBatch = models.BooleanField(default=False)
    can_form_build = models.BooleanField(default=False)
    can_fm = models.BooleanField(default=False)
    can_costing_dashboard = models.BooleanField(default=False)
    can_workflow_access = models.BooleanField(default=False)
    # Folder permissions
    can_goods_entry = models.BooleanField(default=False)
    can_tests = models.BooleanField(default=False)
    can_audit = models.BooleanField(default=False)

    can_delete = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_signature_btn = models.BooleanField(default=False)
    can_approved_document = models.BooleanField(default=False)
    
    can_sign_prepared = models.BooleanField(default=False)
    can_sign_reviewed = models.BooleanField(default=False)
    can_sign_approved = models.BooleanField(default=False)
    allowed_folders = models.ManyToManyField(
        "FormFolder",
        blank=True,
        related_name="permitted_users"
    )

    def __str__(self):
        return f"Access - {self.user.email}"









# ===============================================================================================================================
# ======================================================== CAPA =================================================================
# ===============================================================================================================================

from django.db import models, transaction
from django.conf import settings
from django.utils import timezone


class CAPA(models.Model):

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("ROOT_CAUSE", "Root Cause Analysis"),
        ("ACTION_IMPLEMENTED", "Action Implemented"),
        ("VERIFICATION", "Effectiveness Verification"),
        ("CLOSED", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    capa_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        editable=False
    )

    related_ncr = models.ForeignKey(
        "NCR",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="capa_actions"
    )

    related_batch_part = models.ForeignKey(
        "BatchPart",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="capa_records"
    )

    title = models.CharField(max_length=255)
    problem_statement = models.TextField()

    # AS9100D Root Cause Depth
    root_cause_analysis = models.TextField(blank=True, null=True)
    five_why_analysis = models.TextField(blank=True, null=True)
    corrective_action = models.TextField(blank=True, null=True)
    preventive_action = models.TextField(blank=True, null=True)
    effectiveness_validation = models.TextField(blank=True, null=True)

    severity_score = models.PositiveIntegerField(default=1)
    occurrence_score = models.PositiveIntegerField(default=1)
    detection_score = models.PositiveIntegerField(default=1)
    risk_score = models.PositiveIntegerField(default=1)

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="MEDIUM"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_capa"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_capa"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    due_date = models.DateField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # =====================================================
    # SAFE SAVE LOGIC
    # =====================================================
    def save(self, *args, **kwargs):

        with transaction.atomic():

            # 🔢 SAFE CAPA NUMBER GENERATION
            if not self.capa_number:

                year = timezone.now().year

                last = (
                    CAPA.objects
                    .select_for_update()
                    .filter(capa_number__startswith=f"AS-CAPA-{year}")
                    .order_by("-id")
                    .first()
                )

                if last and last.capa_number:
                    last_seq = int(last.capa_number.split("-")[-1])
                    new_seq = last_seq + 1
                else:
                    new_seq = 1

                self.capa_number = f"AS-CAPA-{year}-{new_seq:04d}"

            #  Risk Calculation
            self.risk_score = (
                self.severity_score *
                self.occurrence_score *
                self.detection_score
            )

            #  Auto Priority Based on Risk
            if self.risk_score >= 200:
                self.priority = "CRITICAL"
            elif self.risk_score >= 120:
                self.priority = "HIGH"
            elif self.risk_score >= 50:
                self.priority = "MEDIUM"
            else:
                self.priority = "LOW"

            # Auto Close Timestamp
            if self.status == "CLOSED" and not self.closed_at:
                self.closed_at = timezone.now()

            super().save(*args, **kwargs)

    # =====================================================
    # UTILITIES
    # =====================================================
    def is_overdue(self):
        if self.due_date and self.status != "CLOSED":
            return timezone.now().date() > self.due_date
        return False

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.capa_number} - {self.title}"





# ===========================================================================================================================
# ====================================================== NCR ================================================================
# ===========================================================================================================================
from django.db import models
from django.conf import settings
from django.utils import timezone


class NCR(models.Model):

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("CONTAINED", "Contained"),
        ("UNDER_INVESTIGATION", "Under Investigation"),
        ("CAPA_REQUIRED", "CAPA Required"),
        ("CLOSED", "Closed"),
        ("ESCAPED_DEFECT", "Escaped Defect"),
    ]

    ncr_number = models.CharField(max_length=30, unique=True, blank=True)

    batch_part = models.ForeignKey(
        "BatchPart",
        on_delete=models.CASCADE,
        related_name="ncr_records"
    )

    form = models.ForeignKey("Form", on_delete=models.SET_NULL, null=True)
    stage = models.ForeignKey("Stage", on_delete=models.SET_NULL, null=True)

    # AS9100D Specific
    product_safety = models.BooleanField(default=False)
    escaped_defect = models.BooleanField(default=False)
    customer_impact = models.BooleanField(default=False)

    description = models.TextField()
    containment_action = models.TextField(blank=True, null=True)

    severity = models.PositiveIntegerField(default=1)
    occurrence = models.PositiveIntegerField(default=1)
    detection = models.PositiveIntegerField(default=1)
    risk_score = models.PositiveIntegerField(default=1)

    recurrence_count = models.PositiveIntegerField(default=1)

    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="OPEN")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # =====================================================
    # SAVE LOGIC
    # =====================================================
    def save(self, *args, **kwargs):

        is_new = self.pk is None

        # 🔢 Generate NCR Number (safe for small systems)
        if not self.ncr_number:
            count = NCR.objects.count() + 1
            self.ncr_number = f"AS-NCR-{timezone.now().year}-{count:04d}"

        # 🔥 Risk Calculation
        self.risk_score = (
            self.severity *
            self.occurrence *
            self.detection
        )

        super().save(*args, **kwargs)

        # 🔴 OPTION 3 LOGIC — MOVE PART TO NCR COLUMN
        if is_new and self.batch_part.status != "NCR":
            self.batch_part.status = "NCR"
            self.batch_part.save(update_fields=["status"])

        # 🔁 Update recurrence count
        self.update_recurrence()

    # =====================================================
    # RECURRENCE LOGIC
    # =====================================================
    def update_recurrence(self):
        count = NCR.objects.filter(batch_part=self.batch_part).count()
        if self.recurrence_count != count:
            self.recurrence_count = count
            super().save(update_fields=["recurrence_count"])

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ncr_number} - {self.batch_part.part_id}"
    
    
class MachineSession(models.Model):

    machine_id = models.CharField(max_length=100)

    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    login_time = models.DateTimeField(auto_now_add=True)

    logout_time = models.DateTimeField(
        null=True,
        blank=True
    )

    shift = models.CharField(
        max_length=20,
        blank=True
    )

    message = models.TextField(
        blank=True, null=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine_id} - {self.operator}"
    

# =========================================================================
    

# =========================================================
# WORK ORDER
# =========================================================

class WorkOrder(models.Model):

    STATUS_CHOICES = [

        ("OPEN", "Open"),

        ("PLANNING", "Planning"),

        ("PRODUCTION", "Production"),

        ("QC", "Quality Check"),

        ("DISPATCH", "Dispatch"),

        ("COMPLETED", "Completed"),

    ]

    # RFQ LINK
    rfq_ref_id = models.CharField(
        max_length=100
    )

    company_name = models.CharField(
        max_length=255
    )

    workorder_id = models.CharField(
        max_length=100,
        unique=True
    )

    priority = models.CharField(
        max_length=50,
        default="MEDIUM"
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    delivery_date = models.DateField(
        null=True,
        blank=True
    )

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

    class Meta:

        ordering = ["-created_at"]

    def __str__(self):

        return self.workorder_id


# =========================================================
# WORK ORDER PART
# =========================================================

class WorkOrderPart(models.Model):

    STATUS_CHOICES = [

        ("INTERNAL_WORKORDER", "Internal Workorder"),

        ("RAW_MATERIAL_PO", "Raw Material Purchase Order"),

        ("RAW_MATERIAL_RECEIVED", "Receive Raw Material"),

        ("PRODUCTION", "Production"),

        ("FINAL_INSPECTION", "Final Inspection"),

        ("DISPATCH", "Dispatch"),

        ("POST_DISPATCH", "Post Dispatch & Feedback"),

    ]

    workorder = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="parts"
    )

    part_id = models.CharField(
        max_length=100
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    material = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    revision = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_workorder_parts"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="INTERNAL_WORKORDER"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    stage_folder = models.ForeignKey(
        FormFolder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    class Meta:

        unique_together = (
            "workorder",
            "part_id"
        )

    def __str__(self):

        return self.part_id
    



# =========================================================
# WORKORDER FORM TRACKING
# =========================================================

class WorkOrderPartFormSubmission(models.Model):

    workorder_item = models.ForeignKey(
        "po_qu.WorkOrderItem",
        on_delete=models.CASCADE,
        related_name="qms_forms",
        null=True,
        blank=True

    )

    form = models.ForeignKey(

        Form,

        on_delete=models.CASCADE

    )

    form_submission = models.ForeignKey(

        FormSubmission,

        on_delete=models.CASCADE,

        null=True,

        blank=True

    )

    submitted_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True

    )

    submitted_at = models.DateTimeField(

        auto_now_add=True

    )

    class Meta:

        unique_together = ("workorder_item", "form")

    def __str__(self):

        if self.workorder_item:
            return f"{self.workorder_item.product_code} - {self.form.name}"

        return self.form.name
