from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.db.models.fields.files import FieldFile
from .models import AuditLog
from qms_app.models import Form, Stage, FormSubmission, QMSDocument
from goods_entry.models import GoodsBatch
from student_test.models import Test
import datetime
import decimal
import uuid

TRACKED_MODELS = [Form, Stage, FormSubmission, QMSDocument, GoodsBatch, Test]

# ==============================
# SERIALIZER
# ==============================
def serialize_instance(instance):
    data = model_to_dict(instance)

    for field, value in data.items():

        if isinstance(value, FieldFile):
            data[field] = value.url if value else None

        elif isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
            data[field] = value.isoformat() if value else None

        elif isinstance(value, decimal.Decimal):
            data[field] = float(value)

        elif isinstance(value, uuid.UUID):
            data[field] = str(value)

    return data


# ==============================
# STORE OLD DATA (BEFORE UPDATE)
# ==============================
@receiver(pre_save)
def store_old_data(sender, instance, **kwargs):

    if sender not in TRACKED_MODELS:
        return

    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_data = serialize_instance(old_instance)
        except sender.DoesNotExist:
            instance._old_data = None


# ==============================
# SAVE LOG (CREATE + UPDATE)
# ==============================
@receiver(post_save)
def log_save(sender, instance, created, **kwargs):

    if sender not in TRACKED_MODELS:
        return

    user = getattr(instance, "created_by", None) or \
           getattr(instance, "submitted_by", None)

    AuditLog.objects.create(
        user=user,
        role=getattr(user, "role", "") if user else "",
        module=sender._meta.app_label,
        action="CREATE" if created else "UPDATE",
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),

        old_data=getattr(instance, "_old_data", None),   # ✅ FIXED
        new_data=serialize_instance(instance)
    )


# ==============================
# DELETE LOG (OPTIONAL SAFE)
# ==============================
@receiver(post_delete)
def log_delete(sender, instance, **kwargs):

    if sender not in TRACKED_MODELS:
        return

    # ⚠️ Prevent bulk spam (like GoodsBatch items)
    if sender.__name__ == "GoodsBatch":
        return

    AuditLog.objects.create(
        user=None,
        module=sender._meta.app_label,
        action="DELETE",
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),
        old_data=serialize_instance(instance)
    )