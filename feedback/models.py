
from django.db import models


class Feedback(models.Model):

    # STATUS CHOICES

    STATUS_CHOICES = [

        ('Open', 'Open'),

        ('Under Investigation', 'Under Investigation'),

        ('CAPA Created', 'CAPA Created'),

        ('Response Sent', 'Response Sent'),

        ('Closed', 'Closed'),

    ]


    # SEVERITY CHOICES

    SEVERITY_CHOICES = [

        ('Low', 'Low'),

        ('Medium', 'Medium'),

        ('High', 'High'),

        ('Critical', 'Critical'),

    ]


    # PRIORITY CHOICES

    PRIORITY_CHOICES = [

        ('Low', 'Low'),

        ('Medium', 'Medium'),

        ('High', 'High'),

        ('Urgent', 'Urgent'),

    ]


    # FEEDBACK TYPE CHOICES

    FEEDBACK_TYPE_CHOICES = [

        ('Complaint', 'Complaint'),

        ('Suggestion', 'Suggestion'),

        ('Appreciation', 'Appreciation'),

        ('Escalation', 'Escalation'),

        ('Delivery Issue', 'Delivery Issue'),

        ('Service Issue', 'Service Issue'),

    ]


    # MAIN DETAILS

    feedback_no = models.CharField(

        max_length=100,

        unique=True

    )

    date_received = models.DateField()

    received_by = models.CharField(

        max_length=255

    )

    customer_name = models.CharField(

        max_length=255

    )

    customer_contact = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    customer_email = models.EmailField(

        blank=True,

        null=True

    )

    product_name = models.CharField(

        max_length=255

    )

    part_number = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    lot_batch_number = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    sales_order_no = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )


    # FEEDBACK DETAILS

    feedback_type = models.CharField(

        max_length=100,

        choices=FEEDBACK_TYPE_CHOICES

    )

    category = models.CharField(

        max_length=255

    )

    severity = models.CharField(

        max_length=50,

        choices=SEVERITY_CHOICES,

        default='Low'

    )

    source_of_feedback = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    reference_document = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    description = models.TextField()


    # FILE ATTACHMENT

    attachment = models.FileField(

        upload_to='feedback/',

        blank=True,

        null=True

    )


    # ADDITIONAL INFORMATION

    date_of_occurrence = models.DateField(

        blank=True,

        null=True

    )

    location_site = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    department = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    impact_on_customer = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    immediate_action_taken = models.TextField(

        blank=True,

        null=True

    )


    # INTERNAL USE

    priority = models.CharField(

        max_length=50,

        choices=PRIORITY_CHOICES,

        default='Medium'

    )

    assigned_to = models.CharField(

        max_length=255,

        blank=True,

        null=True

    )

    target_investigation_date = models.DateField(

        blank=True,

        null=True

    )

    remarks = models.TextField(

        blank=True,

        null=True

    )


    # STATUS TRACKING

    status = models.CharField(

        max_length=50,

        choices=STATUS_CHOICES,

        default='Open'

    )

    due_date = models.DateField(

        blank=True,

        null=True

    )


    # NOTIFICATION

    notify_users = models.BooleanField(

        default=False

    )


    # SYSTEM FIELDS

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    updated_at = models.DateTimeField(

        auto_now=True

    )


    def __str__(self):

        return self.feedback_no
