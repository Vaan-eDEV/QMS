from django.db import models
from django.conf import settings
from decimal import Decimal
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
import uuid
from goods_entry.models import Product

class PurchaseOrder(models.Model):

    # 🔹 Basic Info
    po_number = models.CharField(max_length=50, unique=True, blank=True)
    reference = models.CharField(max_length=255, blank=True)
    date = models.DateField()

    # 🔹 Supplier Info
    supplier_name = models.CharField(max_length=255)
    supplier_address = models.TextField()
    supplier_phone = models.CharField(max_length=20, blank=True)
    supplier_gstin = models.CharField(max_length=50, blank=True)

    # 🔹 Billing Info
    billing_name = models.CharField(max_length=255)
    billing_address = models.TextField()
    billing_phone = models.CharField(max_length=20)
    billing_gstin = models.CharField(max_length=50)

    # 🔹 Shipping Info
    shipping_name = models.CharField(max_length=255)
    shipping_address = models.TextField()
    shipping_phone = models.CharField(max_length=20)
    shipping_gstin = models.CharField(max_length=50)

    # 🔹 Financial Fields
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    cgst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    sgst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    igst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # 🔹 QR Code
    qr_code = models.ImageField(upload_to='po_qr/', blank=True, null=True)

    # 🔹 Notes & Terms
    note = models.TextField(blank=True)
    terms = models.TextField(blank=True)

    # 🔹 Status
    status = models.CharField(
        max_length=30,
        choices=[
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('sent', 'Sent'),
            ('partial_received', 'Partially Received'),
            ('received', 'Received')
        ],
        default='draft'
    )
   
    # 🔹 USERS (EXISTING)
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="po_prepared"
    )
    # 🔥 REVIEWED BY
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="po_reviewed"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="po_approved"
    )

    # 🔥 NEW SIGNATURE FIELDS
    prepared_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True,blank=True)

    prepared_signature_id = models.CharField(max_length=100, blank=True)
    approved_signature_id = models.CharField(max_length=100, blank=True)
    reviewed_signature_id = models.CharField(max_length=100,blank=True)
    digital_id = models.CharField(max_length=100, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.po_number

    # ==============================
    # DIGITAL ID
    # ==============================
    def generate_digital_id(self):
        if not self.digital_id:
            self.digital_id = f"PO-{uuid.uuid4().hex[:12].upper()}"

    # ==============================
    # CALCULATE TOTALS
    # ==============================
    def calculate_totals(self):
        items = self.items.all()

        subtotal = sum((item.amount for item in items), Decimal('0'))

        discount_percentage = Decimal(self.discount_percentage or 0)
        cgst_percentage = Decimal(self.cgst_percentage or 0)
        sgst_percentage = Decimal(self.sgst_percentage or 0)
        igst_percentage = Decimal(self.igst_percentage or 0)

        discount_amount = subtotal * (discount_percentage / Decimal('100'))
        taxable = subtotal - discount_amount

        cgst = taxable * (cgst_percentage / Decimal('100'))
        sgst = taxable * (sgst_percentage / Decimal('100'))
        igst = taxable * (igst_percentage / Decimal('100'))

        grand_total = taxable + cgst + sgst + igst

        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.cgst_amount = cgst
        self.sgst_amount = sgst
        self.igst_amount = igst
        self.grand_total = grand_total

    # ==============================
    # QR CODE
    # ==============================
    def generate_qr_code(self):
        qr_data = f"""
PO Number: {self.po_number}
Supplier: {self.supplier_name}
Date: {self.date}
Total: {self.grand_total}
"""
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        file_name = f"{self.po_number}_qr.png"
        self.qr_code.save(file_name, File(buffer), save=False)

    # ==============================
    # SAVE
    # ==============================
    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        # PO number
        if is_new and not self.po_number:
            self.po_number = f"PO{self.id:04d}"
            super().save(update_fields=['po_number'])

        # totals
        self.calculate_totals()

        # QR
        if not self.qr_code:
            self.generate_qr_code()

        # 🔥 DIGITAL ID
        self.generate_digital_id()

        super().save(update_fields=[
            'subtotal', 'discount_amount',
            'cgst_amount', 'sgst_amount',
            'igst_amount', 'grand_total',
            'qr_code', 'digital_id'
        ])
class PurchaseOrderItem(models.Model):

    po = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    product_code = models.CharField(max_length=100)

    description = models.TextField()

    unit = models.CharField(max_length=50)

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # NEW FIELD
    received_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True
    )

    @property
    def balance_quantity(self):
        return self.quantity - self.received_quantity

    def save(self, *args, **kwargs):

        self.amount = self.quantity * self.rate

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_code} ({self.po.po_number})"
# ==================================================================================================
# ================================== Quotation Main Model ==========================================
# ==================================================================================================


class Quotation(models.Model):

    # 🔹 Basic Info
    quotation_number = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField()
    valid_till = models.DateField(null=True, blank=True)
    reference = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    rfq_id = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)

    # 🔹 Customer
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_address = models.TextField()
    customer_gstin = models.CharField(max_length=50, blank=True)

    # 🔹 Financial
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    cgst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    sgst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    igst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qr_code = models.ImageField(
        upload_to="quotation_qr/",
        blank=True,
        null=True
    )
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # 🔹 Notes
    note = models.TextField(blank=True)
    terms = models.TextField(blank=True)

    # 🔹 Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='draft'
    )

    # 🔹 USERS
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    # 🔥 DIGITAL SIGNATURE FIELDS
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="qt_prepared"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qt_approved"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qt_reviewed"
    )

    prepared_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True,blank=True)

    is_signed = models.BooleanField(default=False)
    prepared_signature_id = models.CharField(max_length=100, blank=True)
    approved_signature_id = models.CharField(max_length=100, blank=True)
    reviewed_signature_id = models.CharField(max_length=100,blank=True)

    digital_id = models.CharField(max_length=100, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.quotation_number

    # ==============================
    # DIGITAL ID
    # ==============================
    def generate_qr_code(self):

        qr_data = f"""
            Quotation Number: {self.quotation_number}
            Customer: {self.customer_name}
            Date: {self.date}
            Grand Total: {self.grand_total}
        """

        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        file_name = f"{self.quotation_number}_qr.png"

        self.qr_code.save(
            file_name,
            File(buffer),
            save=False
        )
    def generate_digital_id(self):
        if not self.digital_id:
            self.digital_id = f"QT-{uuid.uuid4().hex[:12].upper()}"

    # ==============================
    # SAVE
    # ==============================
    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Generate quotation number
        if is_new and not self.quotation_number:
            self.quotation_number = f"QT{self.id:04d}"
            super().save(update_fields=['quotation_number'])

        # Calculate totals
        self.calculate_totals()

        # Generate digital ID
        self.generate_digital_id()

        # Generate QR Code
        if not self.qr_code:
            self.generate_qr_code()

        super().save(update_fields=[
            'subtotal',
            'discount_amount',
            'cgst_amount',
            'sgst_amount',
            'igst_amount',
            'grand_total',
            'digital_id',
            'qr_code'
        ])
    # ==============================
    # CALCULATE TOTALS
    # ==============================
    def calculate_totals(self):

        items = self.items.all()

        subtotal = sum((item.amount for item in items), Decimal('0'))

        discount_percentage = Decimal(self.discount_percentage or 0)
        cgst_percentage = Decimal(self.cgst_percentage or 0)
        sgst_percentage = Decimal(self.sgst_percentage or 0)
        igst_percentage = Decimal(self.igst_percentage or 0)

        discount_amount = subtotal * (discount_percentage / Decimal('100'))
        taxable = subtotal - discount_amount

        cgst = taxable * (cgst_percentage / Decimal('100'))
        sgst = taxable * (sgst_percentage / Decimal('100'))
        igst = taxable * (igst_percentage / Decimal('100'))

        grand_total = taxable + cgst + sgst + igst

        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.cgst_amount = cgst
        self.sgst_amount = sgst
        self.igst_amount = igst
        self.grand_total = grand_total


# ==============================
# ITEMS
# ==============================
class QuotationItem(models.Model):

    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="items"
    )

    part_id = models.TextField()
    part_name = models.CharField(max_length=50, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)

    def _str_(self):
        return self.description




# =====================================================================================================
# ====================================== DC ===========================================================
# =====================================================================================================



class DeliveryChallan(models.Model):

    dc_number = models.CharField(max_length=20, unique=True, blank=True)
    date = models.DateField()
    transporter = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    # FROM
    from_name = models.CharField(max_length=255)
    from_address = models.TextField()
    from_city = models.CharField(max_length=100, blank=True, null=True)
    from_state = models.CharField(max_length=100, blank=True, null=True)
    from_pincode = models.CharField(max_length=20, blank=True, null=True)
    from_country = models.CharField(max_length=100, blank=True, null=True)
    from_phone = models.CharField(max_length=20, blank=True, null=True)
    from_email = models.EmailField(blank=True, null=True)

    # TO
    to_name = models.CharField(max_length=255)
    to_address = models.TextField()
    to_city = models.CharField(max_length=100, blank=True, null=True)
    to_state = models.CharField(max_length=100, blank=True, null=True)
    to_pincode = models.CharField(max_length=20, blank=True, null=True)
    to_country = models.CharField(max_length=100, blank=True, null=True)
    to_phone = models.CharField(max_length=20, blank=True, null=True)
    to_email = models.EmailField(blank=True, null=True)

    qr_code = models.ImageField( upload_to="dc_qr/", blank=True, null=True )
    note = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    # 🔥 DIGITAL SIGNATURE FIELDS
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dc_prepared"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dc_approved"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dc_reviewed"
    )

    prepared_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True,blank=True)


    prepared_signature_id = models.CharField(max_length=100, blank=True)
    approved_signature_id = models.CharField(max_length=100, blank=True)
    reviewed_signature_id = models.CharField(max_length=100,blank=True)

    digital_id = models.CharField(max_length=100, unique=True, blank=True)

    def _str_(self):
        return self.dc_number

    # ==============================
    # DIGITAL ID
    # ==============================
    def generate_digital_id(self):
        if not self.digital_id:
            self.digital_id = f"DC-{uuid.uuid4().hex[:12].upper()}"
    def generate_qr_code(self):

        qr_data = f"""
            Delivery Challan Number: {self.dc_number}
            Date: {self.date}

            From: {self.from_name}

            To: {self.to_name}

            Digital ID: {self.digital_id}
            """

        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        self.qr_code.save(
            f"{self.dc_number}_qr.png",
            File(buffer),
            save=False
        )
    # ==============================
    # SAVE
    # ==============================
    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Generate DC Number
        if is_new and not self.dc_number:
            self.dc_number = f"DC-{self.id:04d}"

            super().save(
                update_fields=["dc_number"]
            )

        # Generate Digital ID
        self.generate_digital_id()

        # Generate QR Code
        if not self.qr_code:
            self.generate_qr_code()

        super().save(
            update_fields=[
                "digital_id",
                "qr_code"
            ]
        )

# ==============================
# ITEMS
# ==============================
class DeliveryChallanItem(models.Model):

    dc = models.ForeignKey(
        DeliveryChallan,
        related_name='items',
        on_delete=models.CASCADE
    )

    product_name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def _str_(self):
        return self.product_name



# ================================================================================
# ===================================== Work Order ===============================
# ================================================================================
class WorkOrder(models.Model):
    wo_number = models.CharField(max_length=50, unique=True, blank=True)
    date = models.DateField()
    customer_name = models.CharField(max_length=255)
    customer_address = models.TextField()
    po_number = models.CharField(max_length=100, blank=True)
    po_date = models.DateField(null=True, blank=True)

    product_notes = models.TextField(blank=True)
    process_notes = models.TextField(blank=True)
    packing_notes = models.TextField(blank=True)
    delivery_notes = models.TextField(blank=True)
    documentation_notes = models.TextField(blank=True)
    other_notes = models.TextField(blank=True, null=True)
    rfq_ref = models.CharField(max_length=200, blank=True, null=True)

    qr_code = models.ImageField(
        upload_to="workorder_qr/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length = 20,
        choices= [
            ('draft', 'Draft'),
            ('prepared', 'Prepared'),
            ('approved', 'Approved'),
        ],
        default= 'draft'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null= True,
        related_name = "po_wo_created"
    )

    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null= True,
        blank=True,
        related_name = "workorders_prepared"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.SET_NULL,
        null= True,
        blank=True,
        related_name = "workorders_approved"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workorders_reviewed"
    )

    prepared_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True,blank=True)

    prepared_signature_id = models.CharField(null=True, blank=True)
    approved_signature_id = models.CharField(null=True, blank=True)
    reviewed_signature_id = models.CharField(max_length=100,blank=True)

    digital_id = models.CharField(max_length=100, unique="True", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wo_number or "WorkOrder"

    def generate_digital_id(self):
        if not self.digital_id:
            self.digital_id = f"WO-{uuid.uuid4().hex[:10].upper()}"

    def generate_qr_code(self):

        qr_data = f"""
            Work Order Number: {self.wo_number}
            Customer: {self.customer_name}
            Date: {self.date}
            Digital ID: {self.digital_id}
        """

        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        file_name = f"{self.wo_number}_qr.png"

        self.qr_code.save(
            file_name,
            File(buffer),
            save=False
        )
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.wo_number:
            self.wo_number = f"WO-{self.id:04d}"
            super().save(update_fields= ['wo_number'])

        self.generate_digital_id()

        if not self.qr_code:
            self.generate_qr_code()

        super().save(
            update_fields=[
                'digital_id',
                'qr_code'
            ]
        )

class WorkOrderItem(models.Model):

    work_order = models.ForeignKey(
        WorkOrder,
        related_name="items",
        on_delete=models.CASCADE
    )

    stage_folder = models.ForeignKey(
        "qms_app.FormFolder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_code = models.CharField(max_length=100)

    product_name = models.CharField(
        max_length=100,
        blank=True
    )

    material = models.CharField(
        max_length=100,
        blank=True
    )

    quantity = models.IntegerField()

    unit = models.CharField(max_length=20)

    STATUS_CHOICES = [

        ("INTERNAL_WORKORDER", "Internal Workorder"),

        ("RFQ_PREP", "RFQ Preparation"),

        ("RAW_MATERIAL_PO", "Raw Material Purchase Order"),

        ("RAW_MATERIAL_RECEIVED", "Receive Raw Material"),

        ("PRODUCTION", "Production"),

        ("FINAL_INSPECTION", "Final Inspection"),

        ("DISPATCH", "Dispatch"),

        ("POST_DISPATCH", "Post Dispatch & Feedback"),

    ]

    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default="INTERNAL_WORKORDER"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_workorder_items"
    )
    rfq_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    rfq_approved = models.BooleanField(
        default=False
    )

    # =========================================================
    # AUTO ASSIGN STAGE FOLDER
    # =========================================================

    def save(self, *args, **kwargs):

        from qms_app.models import FormFolder

        folder_mapping = {

            "INTERNAL_WORKORDER":
                "Internal Workorder",

            "RFQ_PREP":
                "RFQ Preparation",

            "RAW_MATERIAL_PO":
                "Raw Material Purchase Order",

            "RAW_MATERIAL_RECEIVED":
                "Receive Raw material",

            "PRODUCTION":
                "Production",

            "FINAL_INSPECTION":
                "Final Inspection",

            "DISPATCH":
                "Dispatch",

            "POST_DISPATCH":
                "Post dispatch & Feed back",

        }

        folder_name = folder_mapping.get(self.status)

        if folder_name:

            self.stage_folder = FormFolder.objects.filter(
                name=folder_name
            ).first()

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.product_code} ({self.work_order.wo_number})"

class WorkOrderDelivery(models.Model):
    item = models.ForeignKey(
        WorkOrderItem,
        related_name = "deliveries",
        on_delete= models.CASCADE
    )

    delivery_date = models.DateField()
    quantity = models.IntegerField()


    def __str__(self):
        return f"{self.delivery_date} - {self.quantity}"






# ================================================================================
# ====================================== RFQ =====================================
# ================================================================================

class RFQ(models.Model):

    # =========================================================
    # BASIC
    # =========================================================

    rfq_number = models.CharField(

        max_length=50,

        unique=True,

        blank=True
    )

    rfq_date = models.DateField()

    required_delivery_date = models.DateField(

        null=True,

        blank=True
    )

    # =========================================================
    # COMPANY
    # =========================================================

    company_name = models.CharField(
        max_length=255
    )

    contact_person = models.CharField(
        max_length=255
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20
    )

    # =========================================================
    # DELIVERY
    # =========================================================

    delivery_location = models.TextField()

    partial_delivery = models.CharField(

        max_length=100,

        blank=True,

        null=True
    )

    # =========================================================
    # TECHNICAL
    # =========================================================

    material_grade = models.CharField(

        max_length=255,

        blank=True
    )

    applicable_standard = models.CharField(

        max_length=255,

        blank=True
    )

    heat_treatment = models.TextField(
        blank=True
    )

    surface_condition = models.TextField(
        blank=True
    )

    packing_traceability = models.TextField(
        blank=True
    )

    certification_requirement = models.TextField(
        blank=True
    )

    counterfeit_prevention = models.TextField(
        blank=True, null=True, default="The supplier shall ensure prevention of counterfeit material and maintain full traceability to the original material manufacturer. Material shall be supplied with proper identification and supporting certification."
    )
    # =========================================================
    # TAX
    # =========================================================

    discount_percentage = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0
    )

    cgst_percentage = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0
    )

    sgst_percentage = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0
    )

    igst_percentage = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0
    )

    # =========================================================
    # COMMERCIAL
    # =========================================================

    freight_terms = models.TextField(

        blank=True,

        default=""
    )

    payment_terms = models.TextField(

        blank=True,

        default=""
    )

    quotation_validity = models.TextField(

        blank=True,

        default=""
    )
    commercial_requirements = models.TextField(
        blank=True,
        default=""
    )
    # =========================================================
    # NOTES
    # =========================================================

    note = models.TextField(
        blank=True
    )

    compliance_statement = models.TextField(
        blank=True,
        default="Please confirm in your quotation that the offered material fully complies with the above technical and commercial requirements."
    )

    # =========================================================
    # STATUS
    # =========================================================

    status = models.CharField(

        max_length=20,

        choices=[

            ("draft", "Draft"),

            ("prepared", "Prepared"),

            ("approved", "Approved"),

            ("sent", "Sent"),

        ],

        default="draft"
    )
    qr_code = models.ImageField(
        upload_to="rfq_qr/",
        blank=True,
        null=True
    )
    # =========================================================
    # USERS
    # =========================================================

    created_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        related_name="rfq_created"
    )

    prepared_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="rfq_prepared"
    )

    approved_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name="rfq_approved"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rfq_reviewed"
    )

    prepared_at = models.DateTimeField(

        null=True,

        blank=True
    )

    approved_at = models.DateTimeField(

        null=True,

        blank=True
    )
    reviewed_at = models.DateTimeField(null=True,blank=True)

    prepared_signature_id = models.CharField(

        max_length=100,

        blank=True
    )

    approved_signature_id = models.CharField(

        max_length=100,

        blank=True
    )
    reviewed_signature_id = models.CharField(max_length=100,blank=True)

    digital_id = models.CharField(

        max_length=100,

        unique=True,

        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # =========================================================
    # STRING
    # =========================================================

    def __str__(self):

        return self.rfq_number

    # =========================================================
    # DIGITAL ID
    # =========================================================

    def generate_digital_id(self):

        if not self.digital_id:

            self.digital_id = (
                f"RFQ-{uuid.uuid4().hex[:12].upper()}"
            )
    def generate_qr_code(self):

        qr_data = f"""
            RFQ Number: {self.rfq_number}
            Company: {self.company_name}
            Contact Person: {self.contact_person}
            RFQ Date: {self.rfq_date}
            Digital ID: {self.digital_id}
        """

        qr = qrcode.make(qr_data)

        buffer = BytesIO()

        qr.save(
            buffer,
            format="PNG"
        )

        file_name = (
            f"{self.rfq_number}_qr.png"
        )

        self.qr_code.save(
            file_name,
            File(buffer),
            save=False
        )
    # =========================================================
    # SAVE
    # =========================================================

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        # RFQ NUMBER

        if is_new and not self.rfq_number:

            self.rfq_number = (
                f"RFQ-{self.id:04d}"
            )

            super().save(
                update_fields=["rfq_number"]
            )

        # DIGITAL ID

        self.generate_digital_id()

        # QR CODE

        if (
            not self.qr_code
            or not self.qr_code.name
        ):

            self.generate_qr_code()

        super().save(
            update_fields=[
                "digital_id",
                "qr_code"
            ]
        )

# ================================================================================
# ==================================== RFQ ITEM ==================================
# ================================================================================

class RFQItem(models.Model):

    rfq = models.ForeignKey(

        RFQ,

        on_delete=models.CASCADE,

        related_name="items"
    )

    material_name = models.CharField(
        max_length=255
    )

    material_code_grade = models.CharField(

        max_length=255,

        blank=True
    )

    material_dimensions = models.CharField(

        max_length=255,

        blank=True
    )

    quantity = models.DecimalField(

        max_digits=10,

        decimal_places=2
    )

    total_weight = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0
    )

    price_per_kg = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        default=0
    )

    total_price = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0
    )

    intended_use = models.CharField(

        max_length=255,

        blank=True
    )

    # =========================================================
    # SAVE
    # =========================================================

    def save(self, *args, **kwargs):

        weight = Decimal(
            self.total_weight or 0
        )

        price = Decimal(
            self.price_per_kg or 0
        )

        self.total_price = (
            weight * price
        )

        super().save(*args, **kwargs)

    # =========================================================
    # STRING
    # =========================================================

    def __str__(self):

        return (

            f"{self.material_name} "

            f"({self.rfq.rfq_number})"
        )



# =========================================================
# RFQ ATTACHMENTS
# =========================================================

class RFQAttachment(models.Model):

    rfq = models.ForeignKey(

        RFQ,

        on_delete=models.CASCADE,

        related_name="attachments"
    )

    file = models.FileField(

        upload_to="rfq_attachments/"
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

        return (

            f"{self.rfq.rfq_number}"

            f" Attachment"
        )


#
# =================================== QA Inspection ========================================
#

class QAInspection(models.Model):

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name="qa_inspections"
    )

    inspection_no = models.CharField(
        max_length=50,
        unique=True
    )

    inspection_date = models.DateField()

    # =====================
    # PART IDENTIFICATION
    # =====================

    part_number = models.CharField(max_length=200)
    revision = models.CharField(max_length=50, blank=True)
    drawing_reference = models.CharField(max_length=200, blank=True)
    cad_model_filename = models.CharField(max_length=255, blank=True)

    batch_lot_no = models.CharField(
        max_length=100,
        blank=True
    )

    inspection_stage = models.CharField(
        max_length=30,
        choices=[
            ("final_release", "Final Release"),
            ("pre_shipment", "Pre Shipment"),
        ]
    )

    # =====================
    # EQUIPMENT
    # =====================

    cmm_model = models.CharField(
        max_length=255,
        blank=True
    )

    cmm_calibration_valid = models.BooleanField(
        default=False
    )

    calibration_expiry = models.DateField(
        null=True,
        blank=True
    )

    program_loaded = models.BooleanField(
        default=False
    )

    program_filename = models.CharField(
        max_length=255,
        blank=True
    )

    drawing_revision_verified = models.BooleanField(
        default=False
    )

    revision_match = models.CharField(
        max_length=100,
        blank=True
    )

    fixture_setup_verified = models.BooleanField(
        default=False
    )

    fixture_id = models.CharField(
        max_length=100,
        blank=True
    )

    environmental_conditions_stable = models.BooleanField(
        default=False
    )

    environmental_log = models.TextField(
        blank=True
    )

    # =====================
    # DISPOSITION
    # =====================

    all_features_within_tolerance = models.BooleanField(
        default=False
    )

    tolerance_remarks = models.TextField(
        blank=True
    )

    surface_condition = models.CharField(
        max_length=20,
        choices=[
            ("ok", "OK"),
            ("damaged", "Damaged"),
        ],
        blank=True
    )

    labeling_verified = models.BooleanField(
        default=False
    )

    ncr_initiated = models.BooleanField(
        default=False
    )

    ncr_number = models.CharField(
        max_length=100,
        blank=True
    )

    hold_tagged = models.BooleanField(
        default=False
    )

    hold_location = models.CharField(
        max_length=255,
        blank=True
    )

    inspector_notified = models.BooleanField(
        default=False
    )

    notification_time = models.DateTimeField(
        null=True,
        blank=True
    )

    remarks = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    # =====================
    # PART IDENTIFICATION
    # =====================

    customer_name = models.CharField(
        max_length=255,
        blank=True
    )

    drawing_revision = models.CharField(
        max_length=100,
        blank=True
    )

    # =====================
    # PART SERIALS
    # =====================

    part1_id = models.CharField(
        max_length=100,
        blank=True
    )

    part2_id = models.CharField(
        max_length=100,
        blank=True
    )

    part3_id = models.CharField(
        max_length=100,
        blank=True
    )

    part4_id = models.CharField(
        max_length=100,
        blank=True
    )

    part5_id = models.CharField(
        max_length=100,
        blank=True
    )

    # =====================
    # DOCUMENTATION
    # =====================

    final_inspection_sheet_completed = models.BooleanField(
        default=False
    )

    final_inspection_sheet_no = models.CharField(
        max_length=100,
        blank=True
    )

    cmm_report_generated = models.BooleanField(
        default=False
    )

    cmm_report_attached = models.BooleanField(
        default=False
    )

    cmm_report_no = models.CharField(
        max_length=255,
        blank=True
    )

    release_authorized = models.BooleanField(
        default=False
    )

    release_authorization_no = models.CharField(
        max_length=100,
        blank=True
    )

    metadata_updated = models.BooleanField(
        default=False
    )

    operator_initials = models.CharField(
        max_length=20,
        blank=True
    )

    metadata_date = models.DateField(
        null=True,
        blank=True
    )
    def __str__(self):
        return self.inspection_no

 

class QAInspectionMeasurement(models.Model):

    inspection = models.ForeignKey(
        QAInspection,
        on_delete=models.CASCADE,
        related_name="measurements"
    )

    # =====================================
    # FEATURE
    # =====================================

    feature_name = models.CharField(
        max_length=255
    )

    specification = models.CharField(
        max_length=255,
        blank=True
    )

    # =====================================
    # PART 1
    # =====================================

    part1_value = models.CharField(
        max_length=50,
        blank=True
    )

    part1_status = models.CharField(
        max_length=10,
        choices=[
            ("PASS", "PASS"),
            ("FAIL", "FAIL")
        ],
        default="PASS"
    )

    # =====================================
    # PART 2
    # =====================================

    part2_value = models.CharField(
        max_length=50,
        blank=True
    )

    part2_status = models.CharField(
        max_length=10,
        choices=[
            ("PASS", "PASS"),
            ("FAIL", "FAIL")
        ],
        default="PASS"
    )

    # =====================================
    # PART 3
    # =====================================

    part3_value = models.CharField(
        max_length=50,
        blank=True
    )

    part3_status = models.CharField(
        max_length=10,
        choices=[
            ("PASS", "PASS"),
            ("FAIL", "FAIL")
        ],
        default="PASS"
    )

    # =====================================
    # PART 4
    # =====================================

    part4_value = models.CharField(
        max_length=50,
        blank=True
    )

    part4_status = models.CharField(
        max_length=10,
        choices=[
            ("PASS", "PASS"),
            ("FAIL", "FAIL")
        ],
        default="PASS"
    )

    # =====================================
    # PART 5
    # =====================================

    part5_value = models.CharField(
        max_length=50,
        blank=True
    )

    part5_status = models.CharField(
        max_length=10,
        choices=[
            ("PASS", "PASS"),
            ("FAIL", "FAIL")
        ],
        default="PASS"
    )

    # =====================================
    # REMARKS
    # =====================================

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.feature_name




class QAInspectionDocument(models.Model):

    DOCUMENT_TYPE_CHOICES = [

        ("final_inspection_sheet", "Final Inspection Sheet"),

        ("cmm_report", "CMM Report"),

        ("ncr", "NCR"),

        ("release_authorization", "Release Authorization"),

        ("metadata", "Metadata Updated"),

        ("other", "Other"),

    ]

    STATUS_CHOICES = [

        ("pending", "Pending"),

        ("completed", "Completed"),

        ("generated", "Generated"),

        ("attached", "Attached"),

        ("logged", "Logged"),

        ("approved", "Approved"),

        ("yes", "Yes"),

        ("no", "No"),

    ]

    inspection = models.ForeignKey(
        QAInspection,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    # =====================================
    # DOCUMENT
    # =====================================

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # =====================================
    # IDENTIFICATION
    # =====================================

    identifier = models.CharField(
        max_length=255,
        blank=True
    )

    revision = models.CharField(
        max_length=50,
        blank=True
    )

    issue_date = models.DateField(
        null=True,
        blank=True
    )

    # =====================================
    # FILE
    # =====================================

    attachment = models.FileField(
        upload_to="qa_documents/",
        blank=True,
        null=True
    )

    # =====================================
    # REMARKS
    # =====================================

    remarks = models.TextField(
        blank=True
    )

    # =====================================
    # AUDIT
    # =====================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.get_document_type_display()} - "
            f"{self.identifier}"
        )