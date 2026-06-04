from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from qms_app.decorators import require_page_permission
from .models import GoodsBatch, GoodsItem
from uuid import uuid4
import json
import base64
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import localtime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from audit_log.models import AuditLog


#====================================================================================================
#========================================= Goods Entry Page =========================================
#====================================================================================================

@require_page_permission("can_goods_entry")
@login_required
def goods_entry_page(request):

    batches = GoodsBatch.objects.order_by("-created_at")[:20]

    return render(request, "goods_entry/entry.html", {
        "batches": batches
    })


#====================================================================================================
#========================================= Save Goods Entry =========================================
#====================================================================================================

@login_required
@require_POST
def save_goods_entry(request):

    try:
        data = json.loads(request.body)

        current_year = datetime.now().year

        with transaction.atomic():
            last_batch = GoodsBatch.objects.filter(
                batch_id__startswith=f"B{current_year}-"
            ).order_by("-batch_id").first()

            if last_batch:
                last_number = int(last_batch.batch_id.split("-")[1])
                new_number = last_number + 1
            else:
                new_number = 1

            new_batch_id = f"B{current_year}-{str(new_number).zfill(3)}"

            image_file = None

            if data.get("image"):
                format, imgstr = data["image"].split(";base64,")
                ext = format.split("/")[-1]

                image_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f"{uuid4()}.{ext}"
                )

            batch = GoodsBatch.objects.create(
                batch_id=new_batch_id,
                from_location=data.get("from"),
                to_location=data.get("to"),
                date=data.get("date"),
                time=data.get("time"),
                transporter=data.get("transporter", ""),
                created_by=request.user,
                image=image_file
            )


            
            for item in data.get("items", []):

                if item.get("product"):   # avoid empty rows
                    GoodsItem.objects.create(
                        batch=batch,
                        product_name=item.get("product"),
                        quantity=item.get("qty") or 0,
                        price=item.get("price") or 0
                    )
            AuditLog.objects.create(
                user=request.user,
                module="Goods Entry",
                action="CREATE",
                object_id=batch.batch_id,
                ip_address=request.META.get("REMOTE_ADDR"),
                description=f"Goods batch created with ID {batch.batch_id}"
            )
        return JsonResponse({
            "status": "success",
            "message": "Goods entry saved successfully",
            "batch_id": new_batch_id
        })


    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
    

# ==============================================================================================
# ======================================= Live Entry Api =======================================
# ==============================================================================================
@login_required
def goods_api(request):

    batches = GoodsBatch.objects.prefetch_related("items") \
                                .order_by("-created_at")[:20]

    data = []
    for batch in batches:

        data.append({
            "batch_id": batch.batch_id,
            "from": batch.from_location,
            "to": batch.to_location,
            "transporter": batch.transporter,
            "status": batch.status,
            "confirmed_by": batch.confirmed_by.email if batch.confirmed_by else "",
            "confirmed_at": batch.confirmed_at.strftime("%Y-%m-%d %H:%M") if batch.confirmed_at else "",
            "image": batch.image.url if batch.image else "",
            "total_items": batch.items.count()
        })

    return JsonResponse(data, safe=False)


# ==============================================================================================
# ===================================== Receivable Page ========================================
# ==============================================================================================
@login_required
def receivable_page(request):
    return render(request, "goods_entry/receivable.html")



@login_required
def get_batch_details(request, batch_id):

    try:
        batch = GoodsBatch.objects.prefetch_related("items") \
                                  .get(batch_id=batch_id)

        items = []

        for item in batch.items.all():
            items.append({
                "id": item.id,
                "product": item.product_name,
                "qty": item.quantity,
                "price": item.price
            })

        return JsonResponse({
            "status": "success",
            "batch_id": batch.batch_id,
            "from": batch.from_location,
            "to": batch.to_location,
            "transporter": batch.transporter,
            "created_at": localtime(batch.created_at).strftime("%Y-%m-%d %H:%M"),
            "status_value": batch.status,
            "confirmed_by": batch.confirmed_by.email if batch.confirmed_by else "",
            "confirmed_at": localtime(batch.confirmed_at).strftime("%Y-%m-%d %H:%M")
                            if batch.confirmed_at else "",
            "items": items
        })

    except GoodsBatch.DoesNotExist:
        return JsonResponse({"status": "error"})



# ==============================================================================================
# ===================================== Confirm Batch ==========================================
# ==============================================================================================
@login_required
@require_POST
def confirm_batch(request, batch_id):

    batch = get_object_or_404(GoodsBatch, batch_id=batch_id)

    batch.status = "Confirmed"
    batch.confirmed_by = request.user
    batch.confirmed_at = timezone.now()
    batch.save()

    AuditLog.objects.create(
        user=request.user,
        module="Goods Entry",
        action="CONFIRM",
        object_id=batch.batch_id,
        ip_address=request.META.get("REMOTE_ADDR"),
        description=f"Goods batch confirmed with ID {batch.batch_id}"
    )

    return JsonResponse({"status": "success"})
