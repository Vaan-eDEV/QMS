from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL


# ================================
# TEST MODEL
# ================================
# ================================
# TEST MODEL
# ================================
class Test(models.Model):

    CATEGORY_CHOICES = [

        (
            "INDUCTION_TRAINING",
            "Induction Training"
        ),

        (
            "ROLE_BASED_TRAINING",
            "Role Based Training"
        ),

        (
            "EXTERNAL_TRAINING",
            "External Training"
        ),

    ]

    # NEW
    TRAINING_TYPE_CHOICES = [

        ("CLASSROOM", "Classroom"),

        ("ONLINE", "Online"),

        ("VIDEO_BASED", "Video Based"),

        ("SELF_LEARNING", "Self Learning"),

        ("PRESENTATION", "Presentation"),

        ("DEMONSTRATION", "Demonstration"),

        ("PRACTICAL", "Practical"),

        ("ON_THE_JOB", "On The Job"),

        ("QUALITY", "Quality"),

        ("TECHNICAL_CERTIFICATION", "Technical Certification"),

        ("AWARENESS", "Awareness"),

    ]

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="INDUCTION_TRAINING"
    )

    # NEW FIELD
    training_type = models.CharField(
        max_length=100,
        choices=TRAINING_TYPE_CHOICES,
        blank=True,
        null=True
    )

    title = models.CharField(
        max_length=200
    )

    duration_minutes = models.PositiveIntegerField(
        default=10
    )

    pass_percentage = models.PositiveIntegerField(
        default=40
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tests"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.category})"

from django.utils import timezone

class StudyMaterial(models.Model):

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="materials"
    )

    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="study_materials/")

    # 🔥 NEW FIELDS
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        """Check if material is currently available"""
        now = timezone.now()

        if self.start_date and now < self.start_date:
            return False

        if self.end_date and now > self.end_date:
            return False

        return True

    def __str__(self):
        return f"{self.test.title} - {self.title}"



class StudyMaterialProgress(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE)

    viewed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "material")
        
        
# ================================
# QUESTION MODEL
# ================================
class Question(models.Model):

    QUESTION_TYPES = [
        ("MCQ", "Choose the Best Answer"),
        ("FILL", "Fill in the Blank"),
        ("BOOL", "Yes / No"),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_text = models.TextField()
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES
    )

    # -------- MCQ --------
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    # -------- MCQ IMAGES --------
    option_a_image = models.ImageField(upload_to="questions/", blank=True, null=True)
    option_b_image = models.ImageField(upload_to="questions/", blank=True, null=True)
    option_c_image = models.ImageField(upload_to="questions/", blank=True, null=True)
    option_d_image = models.ImageField(upload_to="questions/", blank=True, null=True)

    correct_option = models.CharField(
        max_length=1,
        blank=True,
        null=True
    )

    # -------- FILL --------
    correct_answer_text = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # -------- YES / NO --------
    correct_boolean = models.BooleanField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def clean(self):
        """
        Validation logic depending on question type
        """

        if self.question_type == "MCQ":
            if not self.correct_option:
                raise ValidationError("MCQ must have a correct option.")
            if not all([self.option_a, self.option_b]):
                raise ValidationError("MCQ must have at least Option A and B.")

        elif self.question_type == "FILL":
            if not self.correct_answer_text:
                raise ValidationError("Fill in the blank must have correct answer text.")

        elif self.question_type == "BOOL":
            if self.correct_boolean is None:
                raise ValidationError("Yes/No question must define correct boolean value.")

    def __str__(self):
        return f"{self.test.title} - {self.question_text[:50]}"



# ================================
# EMPLOYEE MODEL
# ================================
from django.db import models
from django.conf import settings


class Employee(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employee_profile"
    )

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]
    profile_image = models.ImageField(
        upload_to="employee_profiles/",
        null=True,
        blank=True
    )
    # ================= BASIC =================
    emp_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    # ================= PERSONAL =================
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    # ================= EXTRA =================
    
    qualification = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # ================= GOVT IDS =================
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    aadhar_number = models.CharField(max_length=20, blank=True, null=True)
    uan_number = models.CharField(max_length=20, blank=True, null=True)
    pf_number = models.CharField(max_length=20, blank=True, null=True)
    esi_number = models.CharField(max_length=20, blank=True, null=True)

    # ================= CONTACT =================
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    alternate_number = models.CharField(max_length=15, blank=True, null=True)

    # ================= ADDRESS =================
    current_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)

    # ================= EMPLOYMENT =================
    department = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    date_of_joining = models.DateField(null=True, blank=True)
    employment_type = models.CharField(max_length=50, blank=True, null=True)
    work_location = models.CharField(max_length=100, blank=True, null=True)
    shift = models.CharField(max_length=50, blank=True, null=True)
    cost_center = models.CharField(max_length=50, blank=True, null=True)
    reporting_manager = models.CharField(max_length=200, blank=True, null=True)

    # ================= BANK =================
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    branch_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    account_type = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    # ================= SALARY =================
    pay_grade = models.CharField(max_length=50, blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField(null=True, blank=True)
    payment_cycle = models.CharField(max_length=20, blank=True, null=True)

    # ================= EMERGENCY =================
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_relationship = models.CharField(max_length=100, blank=True, null=True)
    emergency_mobile = models.CharField(max_length=15, blank=True, null=True)
    emergency_alternate = models.CharField(max_length=15, blank=True, null=True)
    emergency_address = models.TextField(blank=True, null=True)

    # ================= META =================
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    pdf_file = models.FileField(upload_to="certificates/pdf/", blank=True, null=True)
    def __str__(self):
        return f"{self.name} ({self.emp_id})"
    
# ================================
# STUDENT RESULT MODEL
# ================================
class StudentResult(models.Model):

    STATUS_CHOICES = [
        ("PASS", "Pass"),
        ("FAIL", "Fail"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="test_results"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results"
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="results"
    )

    score = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    percentage = models.FloatField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    completed_at = models.DateTimeField(auto_now_add=True)

    # Stores answers like:
    # { "1": "A", "2": "Yes", "3": "python" }
    answers = models.JSONField(default=dict)

    class Meta:
        unique_together = ("student", "test")
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.student} - {self.test.title}"
    
    
# ========================================== Employee detail model ============================================
# ================================
# EMPLOYEE CERTIFICATES
# ================================
class EmployeeCertificate(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    certificate_name = models.CharField(max_length=200)

    file = models.FileField(upload_to="employee_certificates/")

    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.certificate_name}"