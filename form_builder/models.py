from django.db import models
from django.conf import settings

# ===============================
# FORM
# ===============================

class Form(models.Model):

    PROCESS_CHOICES = [
        ("RFQ", "RFQ"),
        ("FEASIBILITY", "Feasibility"),
        ("COSTING", "Costing"),
        ("REGISTER", "Register"),
        ("PROPOSAL", "Proposal"),
    ]

    name = models.CharField(max_length=200)

    process = models.CharField(
        max_length=50,
        choices=PROCESS_CHOICES,
        default="RFQ"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="builder_forms",null=True,blank=True,)
    is_active = models.BooleanField(default=False) 
    def __str__(self):
        return f"{self.name} ({self.process})"


# ===============================
# STAGE
# ===============================

class Stage(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.name


# ===============================
# FIELD
# ===============================

class Field(models.Model):

    FIELD_TYPES = [
        ("text", "Text"),
        ("textarea", "Textarea"),
        ("number", "Number"),
        ("date", "Date"),
        ("percentage", "Percentage"),
        ("formula", "Formula"),
        ("table", "Table"),
        ("select", "Select"),
        ("checkbox", "Checkbox"),
        ("signature", "Signature"),
        ("link", "Link"),
        ("file", "File Upload"),
        ("image", "Image Upload"),
    ]

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)

    label = models.CharField(max_length=200)

    field_type = models.CharField(
        max_length=50,
        choices=FIELD_TYPES
    )

    formula = models.TextField(blank=True, null=True)

    options = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    order = models.IntegerField(default=0)
    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label


# ===============================
# TABLE
# ===============================

class Table(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)

    layout_type = models.CharField(
        max_length=20,
        choices=[
            ("column", "Column Based"),
            ("row", "Row Based"),
            ("matrix", "Matrix Based")
        ],
        default="column"
    )

    row_count = models.IntegerField(default=1)
    row_header_name = models.CharField(
        max_length = 255,
        default = "Row Name"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    order = models.IntegerField(default=0)
    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


# ===============================
# TABLE COLUMN
# ===============================

class TableColumn(models.Model):

    COLUMN_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("percentage", "Percentage"),
        ("formula", "Formula"),
        ("signature", "Signature"),
        ("date", "Date"),
        ("link", "Link"),
        ("file", "File Upload"),
        ("image", "Image Upload"),
        ("select", "Select"),
        ("checkbox", "Checkbox"),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE)

    name = models.CharField(max_length=1500)

    column_type = models.CharField(
        max_length=50,
        choices=COLUMN_TYPES
    )
    options = models.TextField(blank=True, null=True,
        help_text = "Comma separate values (e.g: Yes,No,maybe)"
    )
    is_total = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    formula = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["order"]



class TableRow(models.Model):

    table = models.ForeignKey(Table, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)

    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class TableCellConfig(models.Model):

    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE
    )

    row = models.ForeignKey(
        TableRow,
        on_delete=models.CASCADE
    )

    column = models.ForeignKey(
        TableColumn,
        on_delete=models.CASCADE
    )

    cell_type = models.CharField(
        max_length=50,
        choices=TableColumn.COLUMN_TYPES
    )

    # =====================================
    # CELL OPTIONS
    # =====================================

    options = models.TextField(
        blank=True,
        null=True
    )

    # =====================================
    # CELL FORMULA
    # =====================================

    formula = models.TextField(
        blank=True,
        null=True
    )

    is_total = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ("row", "column")

    def __str__(self):

        return f"{self.row} - {self.column}"


# ===============================
# FORM RESPONSE (✅ FIXED)
# ===============================

class FormResponse(models.Model):

    form = models.ForeignKey(Form, on_delete=models.CASCADE)

    ref_id = models.CharField(max_length=100, blank=True, null=True)   # ✅ CORRECT PLACE
    company = models.CharField(max_length=255, blank=True, null=True)
    data = models.JSONField()
    doc_name = models.CharField(max_length=255, blank=True, null=True)
    doc_number = models.CharField(max_length=255, blank=True, null=True)
    revision = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_costing_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null = True,
        blank=True,
        on_delete = models.SET_NULL,
        related_name= "costing_approved_by"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(max_length=50, default="PROPOSAL")

    is_reviewed = models.BooleanField(default=False)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="won_reviewed_by"
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together = ("ref_id", "company", "form")