from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL


# ================================
# TEST MODEL
# ================================
class Test(models.Model):

    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(default=10)
    pass_percentage = models.PositiveIntegerField(default=40)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tests"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


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
