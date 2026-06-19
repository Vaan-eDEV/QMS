from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL





class ProductCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name


class Product(models.Model):

    product_code = models.CharField(
        max_length=100,
        unique=True
    )

    product_name = models.CharField(
        max_length=255
    )

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products"
    )

    unit = models.CharField(
        max_length=50
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product_code} - {self.product_name}"
# ====================================================================================
# GOODS BATCH
# ====================================================================================

class GoodsBatch(models.Model):

    batch_id = models.CharField(
        max_length=50,
        unique=True
    )

    # PO Reference
    po_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    from_location = models.CharField(
        max_length=100
    )

    to_location = models.CharField(
        max_length=100
    )

    transporter = models.CharField(
        max_length=100,
        blank=True
    )

    date = models.DateField()

    time = models.TimeField()

    image = models.ImageField(
        upload_to="goods/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="confirmed_batches"
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_batches"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.batch_id


# ====================================================================================
# GOODS ITEM
# ====================================================================================

class GoodsItem(models.Model):

    batch = models.ForeignKey(
        GoodsBatch,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    product_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    product_name = models.CharField(
        max_length=200
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.product_name








# ====================================================================================
# INVENTORY MASTER
# ====================================================================================

class Inventory(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    product_code = models.CharField(
        max_length=100,
        unique=True
    )

    product_name = models.CharField(
        max_length=255
    )

    stock_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

# ====================================================================================
# INVENTORY TRANSACTION / STOCK LEDGER
# ====================================================================================

class InventoryTransaction(models.Model):

    TRANSACTION_TYPES = (
        ("IN", "IN"),
        ("OUT", "OUT"),
    )

    product_code = models.CharField(
        max_length=100
    )

    product_name = models.CharField(
        max_length=255
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    reference_no = models.CharField(
        max_length=100
    )

    remarks = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product_code} - {self.transaction_type}"



class MaterialIssue(models.Model):

    workorder_item = models.ForeignKey(
        "po_qu.WorkOrderItem",
        on_delete=models.CASCADE,
        related_name="material_issues"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    product_code = models.CharField(
        max_length=100
    )

    product_name = models.CharField(
        max_length=255
    )

    issued_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    issued_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product_code} - {self.issued_qty}"