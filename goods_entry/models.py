from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


from django.utils import timezone

class GoodsBatch(models.Model):

    batch_id = models.CharField(max_length=50, unique=True)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    transporter = models.CharField(max_length=100, blank=True)

    date = models.DateField()
    time = models.TimeField()

    image = models.ImageField(upload_to="goods/", blank=True, null=True)

    #  NEW FIELDS
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

    confirmed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_batches"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.batch_id



class GoodsItem(models.Model):
    batch = models.ForeignKey(
        GoodsBatch,
        related_name="items",
        on_delete=models.CASCADE
    )

    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_name
