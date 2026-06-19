from django.db import models
from django.conf import settings
from django.utils import timezone

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
    # RISK CLASSIFICATION
    # =====================================

    risk_score = models.IntegerField(
        default=0
    )

    risk_category = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    review_frequency = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    business_impact = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    criticality = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    supply_risk = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    quality_risk = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    compliance_risk = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    financial_risk = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    geographical_risk = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    risk_comments = models.TextField(
        blank=True,
        null=True
    )

    mitigation_plan = models.TextField(
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
    document_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
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

    # =====================================
    # EVALUATION CRITERIA (1-5 SCORE)
    # =====================================

    quality_score = models.IntegerField(
        default=0
    )

    delivery_score = models.IntegerField(
        default=0
    )

    cost_score = models.IntegerField(
        default=0
    )

    communication_score = models.IntegerField(
        default=0   
    )

    documentation_score = models.IntegerField(
        default=0
    )

    technical_score = models.IntegerField(
        default=0
    )

    qms_score = models.IntegerField(
        default=0
    )

    # =====================================
    # CALCULATED VALUES
    # =====================================

    weighted_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )

    total_score = models.IntegerField(
        default=0
    )

    # =====================================
    # RESULT
    # =====================================

    rating = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    approval_status = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    approved = models.BooleanField(
        default=False
    )

    # =====================================
    # SUMMARY
    # =====================================

    strengths = models.TextField(
        blank=True,
        null=True
    )

    weak_areas = models.TextField(
        blank=True,
        null=True
    )

    corrective_actions = models.TextField(
        blank=True,
        null=True
    )

    next_evaluation_date = models.DateField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    # =====================================
    # AUDIT INFO
    # =====================================

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

    # =====================================
    # AUTO CALCULATION
    # =====================================

    def save(self, *args, **kwargs):

        self.weighted_score = (

            (self.quality_score * 30) +

            (self.delivery_score * 20) +

            (self.cost_score * 10) +

            (self.communication_score * 10) +

            (self.documentation_score * 10) +

            (self.technical_score * 10) +

            (self.qms_score * 10)

        ) / 100

        self.percentage = round(
            (self.weighted_score / 5) * 100,
            2
        )

        self.total_score = int(
            self.percentage
        )

        if self.percentage >= 90:

            self.rating = "Excellent"
            self.approval_status = "Fully Approved"
            self.approved = True

        elif self.percentage >= 75:

            self.rating = "Good"
            self.approval_status = "Approved"
            self.approved = True

        elif self.percentage >= 60:

            self.rating = "Moderate"
            self.approval_status = "Conditionally Approved"

        else:

            self.rating = "Poor"
            self.approval_status = "Not Approved"

        super().save(*args, **kwargs)

    def __str__(self):

        return f"Evaluation - {self.supplier.supplier_name}"







# =========================================================
# SUPPLIER AUDIT REQUEST
# =========================================================

class SupplierAuditRequest(models.Model):

    STATUS_CHOICES = [

        ('draft', 'Draft'),

        ('submitted', 'Submitted'),

        ('approved', 'Approved'),

        ('rejected', 'Rejected'),

        ('planned', 'Planned'),

        ('scheduled', 'Scheduled'),

        ('completed', 'Completed'),

        ('closed', 'Closed'),

    ]

    AUDIT_TYPE_CHOICES = [

        ('initial', 'Initial Qualification Audit'),

        ('surveillance', 'Surveillance Audit'),

        ('requalification', 'Requalification Audit'),

        ('special', 'Special Audit'),

        ('followup', 'Follow-up Audit'),

    ]

    AUDIT_CRITERIA_CHOICES = [

        ('iso9001', 'ISO 9001:2015'),

        ('iatf16949', 'IATF 16949'),

        ('iso13485', 'ISO 13485'),

        ('iso14001', 'ISO 14001'),

        ('iso45001', 'ISO 45001'),

        ('customer', 'Customer Requirement'),

        ('internal', 'Internal Supplier Standard'),

    ]

    PRIORITY_CHOICES = [

        ('low', 'Low'),

        ('medium', 'Medium'),

        ('high', 'High'),

        ('critical', 'Critical'),

    ]

    TRIGGER_CHOICES = [

        ('periodic', 'Periodic Audit'),

        ('complaint', 'Customer Complaint'),

        ('new_supplier', 'New Supplier Qualification'),

        ('performance', 'Poor Supplier Performance'),

        ('capa', 'CAPA Verification'),

        ('management', 'Management Decision'),

        ('regulatory', 'Regulatory Requirement'),

    ]
    AUDIT_CATEGORY_CHOICES = [

        ('onsite', 'On-site Audit'),

        ('remote', 'Remote Audit'),

        ('hybrid', 'Hybrid Audit'),

    ]
    request_no = models.CharField(
        max_length=30,
        unique=True
    )
    current_step = models.IntegerField(
        default=1
    )
    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.CASCADE,
        related_name='audit_requests'
    )
    supplier_code_snapshot = models.CharField(
        max_length=100,
        blank=True
    )

    supplier_name_snapshot = models.CharField(
        max_length=255,
        blank=True
    )
    audit_type = models.CharField(
        max_length=50,
        choices=AUDIT_TYPE_CHOICES
    )
    audit_category = models.CharField(
        max_length=20,
        choices=AUDIT_CATEGORY_CHOICES,
        default='onsite'
    )
    audit_criteria = models.CharField(
        max_length=50,
        choices=AUDIT_CRITERIA_CHOICES
    )

    audit_trigger = models.CharField(
        max_length=50,
        choices=TRIGGER_CHOICES
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    preferred_audit_date = models.DateField()

    reason = models.TextField()

    objectives = models.TextField()

    additional_notes = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supplier_audit_requests'
    )

    requested_date = models.DateTimeField(
        auto_now_add=True
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_supplier_audits'
    )

    approved_date = models.DateTimeField(
        null=True,
        blank=True
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    def save(self, *args, **kwargs):

        if not self.request_no:

            year = timezone.now().year

            last_record = SupplierAuditRequest.objects.filter(
                request_no__startswith=f"SAR-{year}"
            ).order_by('-id').first()

            if last_record:

                last_no = int(
                    last_record.request_no.split('-')[-1]
                ) + 1

            else:

                last_no = 1

            self.request_no = (
                f"SAR-{year}-{last_no:04d}"
            )

        if self.supplier:

            self.supplier_code_snapshot = (
                self.supplier.supplier_code
            )

            self.supplier_name_snapshot = (
                self.supplier.supplier_name
            )

        super().save(*args, **kwargs)
    def __str__(self):
        return self.request_no




class AuditScopeMaster(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


class DepartmentMaster(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name  

class DeliverableMaster(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name
# =========================================================
# AUDIT SCOPE
# =========================================================

class SupplierAuditScope(models.Model):

    audit_request = models.ForeignKey(
        SupplierAuditRequest,
        on_delete=models.CASCADE,
        related_name='scopes'
    )

    scope = models.ForeignKey(
        AuditScopeMaster,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.scope)


# =========================================================
# DEPARTMENTS TO VISIT
# =========================================================

class SupplierAuditDepartment(models.Model):

    audit_request = models.ForeignKey(
        SupplierAuditRequest,
        on_delete=models.CASCADE,
        related_name='departments'
    )

    department = models.ForeignKey(
        DepartmentMaster,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.department)


# =========================================================
# EXPECTED DELIVERABLES
# =========================================================

class SupplierAuditDeliverable(models.Model):

    audit_request = models.ForeignKey(
        SupplierAuditRequest,
        on_delete=models.CASCADE,
        related_name='deliverables'
    )

    deliverable = models.ForeignKey(
        DeliverableMaster,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.deliverable)


# =========================================================
# ATTACHMENTS
# =========================================================

class SupplierAuditAttachment(models.Model):

    audit_request = models.ForeignKey(
        SupplierAuditRequest,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    file = models.FileField(
        upload_to='supplier_audits/'
    )

    description = models.CharField(
        max_length=255,
        blank=True
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
        return self.file.name


# =========================================================
# AUDIT APPROVAL HISTORY
# =========================================================

class SupplierAuditApprovalHistory(models.Model):

    ACTION_CHOICES = [

        ('submitted', 'Submitted'),

        ('approved', 'Approved'),

        ('rejected', 'Rejected'),

        ('planned', 'Planned'),

        ('closed', 'Closed'),

    ]

    audit_request = models.ForeignKey(
        SupplierAuditRequest,
        on_delete=models.CASCADE,
        related_name='approval_history'
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES
    )

    comments = models.TextField(
        blank=True
    )

    action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    action_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.audit_request.request_no} - {self.action}"

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