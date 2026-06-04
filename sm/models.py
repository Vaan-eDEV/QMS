from django.db import models
from django.conf import settings


# =========================================================
# SUPPLIER MAIN MODEL
# =========================================================

class Supplier(models.Model):

    STATUS_CHOICES = [

        ('draft', 'Draft'),

        ('in_progress', 'In Progress'),

        ('approved', 'Approved'),

        ('rejected', 'Rejected'),

    ]

    SUPPLIER_TYPE_CHOICES = [

        ('manufacturer', 'Manufacturer'),

        ('service_provider', 'Service Provider'),

        ('trader', 'Trader'),

        ('contractor', 'Contractor'),

    ]

    RISK_LEVEL_CHOICES = [

        ('low', 'Low'),

        ('medium', 'Medium'),

        ('high', 'High'),

        ('critical', 'Critical'),

    ]

    # =====================================
    # BASIC DETAILS
    # =====================================

    supplier_code = models.CharField(
        max_length=50,
        unique=True
    )

    supplier_name = models.CharField(
        max_length=255
    )

    supplier_type = models.CharField(
        max_length=50,
        choices=SUPPLIER_TYPE_CHOICES
    )

    category = models.CharField(
        max_length=255
    )

    # =====================================
    # CONTACT DETAILS
    # =====================================

    contact_person = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    # =====================================
    # ADDRESS
    # =====================================

    address = models.TextField(
        blank=True,
        null=True
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # =====================================
    # BUSINESS DETAILS
    # =====================================

    gst_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    pan_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # =====================================
    # EVALUATION DETAILS
    # =====================================

    evaluation_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='low'
    )

    audit_status = models.CharField(
        max_length=100,
        default='Pending'
    )

    next_review_date = models.DateField(
        blank=True,
        null=True
    )

    # =====================================
    # WORKFLOW
    # =====================================

    current_stage = models.IntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    is_active = models.BooleanField(
        default=True
    )

    # =====================================
    # SYSTEM FIELDS
    # =====================================

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_suppliers'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =====================================
    # DISPLAY
    # =====================================

    def __str__(self):

        return f"{self.supplier_code} - {self.supplier_name}"


# =========================================================
# SUPPLIER WORKFLOW STAGES
# =========================================================

class SupplierStage(models.Model):

    STAGE_STATUS_CHOICES = [

        ('pending', 'Pending'),

        ('in_progress', 'In Progress'),

        ('completed', 'Completed'),

        ('rejected', 'Rejected'),

    ]

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='stages'
    )

    stage_no = models.IntegerField()

    stage_name = models.CharField(
        max_length=255
    )

    status = models.CharField(
        max_length=20,
        choices=STAGE_STATUS_CHOICES,
        default='pending'
    )

    assigned_department = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    completed_date = models.DateField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ['stage_no']

    def __str__(self):

        return f"{self.supplier.supplier_code} - {self.stage_name}"


# =========================================================
# SUPPLIER DOCUMENTS
# =========================================================

class SupplierDocument(models.Model):

    DOCUMENT_STATUS_CHOICES = [

        ('pending', 'Pending'),

        ('approved', 'Approved'),

        ('rejected', 'Rejected'),

    ]

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    document_name = models.CharField(
        max_length=255
    )

    document_file = models.FileField(
        upload_to='supplier_documents/'
    )

    version = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    expiry_date = models.DateField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=DOCUMENT_STATUS_CHOICES,
        default='pending'
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.document_name


# =========================================================
# SUPPLIER EVALUATION SCORECARD
# =========================================================

class SupplierEvaluation(models.Model):

    supplier = models.OneToOneField(
        Supplier,
        on_delete=models.CASCADE,
        related_name='evaluation'
    )

    quality_score = models.IntegerField(
        default=0
    )

    delivery_score = models.IntegerField(
        default=0
    )

    technical_score = models.IntegerField(
        default=0
    )

    documentation_score = models.IntegerField(
        default=0
    )

    compliance_score = models.IntegerField(
        default=0
    )

    commercial_score = models.IntegerField(
        default=0
    )

    total_score = models.IntegerField(
        default=0
    )

    approved = models.BooleanField(
        default=False
    )

    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    evaluated_at = models.DateTimeField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):

        self.total_score = (

            self.quality_score +

            self.delivery_score +

            self.technical_score +

            self.documentation_score +

            self.compliance_score +

            self.commercial_score

        )

        super().save(*args, **kwargs)

    def __str__(self):

        return f"Evaluation - {self.supplier.supplier_name}"


# =========================================================
# SUPPLIER AUDIT
# =========================================================

class SupplierAudit(models.Model):

    AUDIT_RESULT_CHOICES = [

        ('pass', 'Pass'),

        ('fail', 'Fail'),

        ('conditional', 'Conditional Approval'),

    ]

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='audits'
    )

    audit_date = models.DateField()

    auditor_name = models.CharField(
        max_length=255
    )

    audit_result = models.CharField(
        max_length=20,
        choices=AUDIT_RESULT_CHOICES
    )

    findings = models.TextField(
        blank=True,
        null=True
    )

    corrective_action = models.TextField(
        blank=True,
        null=True
    )

    next_audit_date = models.DateField(
        blank=True,
        null=True
    )

    audit_report = models.FileField(
        upload_to='supplier_audits/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.supplier.supplier_name} Audit"


# =========================================================
# APPROVALS
# =========================================================

class SupplierApproval(models.Model):

    APPROVAL_STATUS_CHOICES = [

        ('pending', 'Pending'),

        ('approved', 'Approved'),

        ('rejected', 'Rejected'),

    ]

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='approvals'
    )

    approval_stage = models.CharField(
        max_length=255
    )

    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending'
    )

    comments = models.TextField(
        blank=True,
        null=True
    )

    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):

        return f"{self.supplier.supplier_name} - {self.approval_stage}"


# =========================================================
# APPROVED SUPPLIER LIST (ASL)
# =========================================================

class ApprovedSupplierList(models.Model):

    supplier = models.OneToOneField(
        Supplier,
        on_delete=models.CASCADE,
        related_name='asl'
    )

    approved_date = models.DateField()

    valid_until = models.DateField()

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"ASL - {self.supplier.supplier_name}"


# =========================================================
# SUPPLIER ACTIVITY HISTORY
# =========================================================

class SupplierActivity(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='activities'
    )

    activity = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ['-created_at']

    def __str__(self):

        return self.activity