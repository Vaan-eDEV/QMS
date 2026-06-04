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
from form_builder.models import (
    Form as FBForm,
    Stage as FBStage,
    Field,
    Table,
    TableColumn,
    FormResponse
)

TRACKED_MODELS = [Form, Stage, FormSubmission, QMSDocument, GoodsBatch, Test, FBForm, FBStage, Field, Table, TableColumn, FormResponse]

# ==============================
# SERIALIZER
# ==============================
from django.db.models import ForeignKey
from django.forms.models import model_to_dict
from django.db.models.fields.files import FieldFile
import datetime, decimal, uuid

def serialize_instance(instance):

    EXCLUDE_FIELDS = ["id"]   # 🔥 keep created_by if you want name

    data = {}

    for field in instance._meta.fields:

        if field.name in EXCLUDE_FIELDS:
            continue

        value = getattr(instance, field.name)

        # ✅ FOREIGN KEY → SHOW NAME (IMPORTANT FIX)
        if isinstance(field, ForeignKey):
            if value:
                data[field.name] = str(value)   # 👈 shows name instead of ID
            else:
                data[field.name] = None

        # ✅ FILE FIELD
        elif isinstance(value, FieldFile):
            data[field.name] = value.url if value else None

        # ✅ DATE / TIME
        elif isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
            data[field.name] = value.isoformat() if value else None

        # ✅ DECIMAL
        elif isinstance(value, decimal.Decimal):
            data[field.name] = float(value)

        # ✅ UUID
        elif isinstance(value, uuid.UUID):
            data[field.name] = str(value)

        # ✅ NORMAL FIELD
        else:
            data[field.name] = value

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

    user = None
    if hasattr(instance, "created_by"):
        user = instance.created_by
    elif hasattr(instance, "submitted_by"):
        user = instance.submitted_by

    AuditLog.objects.create(
        user=user,
        role=getattr(user, "role", "") if user else "",
        module=sender._meta.app_label,
        action="CREATE" if created else "UPDATE",
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),

        description=f"{sender.__name__} {'created' if created else 'updated'}",

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
        user=getattr(instance, "created_by", None),
        module=sender._meta.app_label,
        action="DELETE",
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),
        old_data=serialize_instance(instance)
    )