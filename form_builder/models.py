from django.db import models


# ===============================
# FORM
# ===============================

class Form(models.Model):

    PROCESS_CHOICES = [
        ("RFQ", "RFQ"),
        ("FEASABILITY", "Feasability"),
        ("COSTING", "Costing"),
    ]

    name = models.CharField(max_length=200)

    process = models.CharField(
        max_length=50,
        choices=PROCESS_CHOICES,
        default="RFQ"
    )

    created_at = models.DateTimeField(auto_now_add=True)
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
    ]

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)

    label = models.CharField(max_length=200)

    field_type = models.CharField(
        max_length=50,
        choices=FIELD_TYPES
    )

    formula = models.TextField(blank=True, null=True)

    options = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.label


# ===============================
# TABLE
# ===============================

class Table(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

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
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)

    column_type = models.CharField(
        max_length=50,
        choices=COLUMN_TYPES
    )

    is_total = models.BooleanField(default=False)

    formula = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ===============================
# FORM RESPONSE (✅ FIXED)
# ===============================

class FormResponse(models.Model):

    form = models.ForeignKey(Form, on_delete=models.CASCADE)

    ref_id = models.CharField(max_length=100, blank=True, null=True)   # ✅ CORRECT PLACE

    data = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)