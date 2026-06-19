from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from qms_app.decorators import require_page_permission
from .models import (
    GoodsBatch,
    GoodsItem,
    Inventory,
    InventoryTransaction,
    Product,
    ProductCategory
)
from po_qu.models import (
    PurchaseOrder,
    PurchaseOrderItem
)
from po_qu.models import WorkOrder, WorkOrderItem
from .models import (
    Inventory,
    InventoryTransaction,
    MaterialIssue
)

from decimal import Decimal
from decimal import Decimal
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
def get_categories(request):

    categories = ProductCategory.objects.all().order_by(
        "name"
    )

    return JsonResponse(
        list(
            categories.values(
                "id",
                "name"
            )
        ),
        safe=False
    )


@login_required
@require_POST
def create_category(request):

    try:

        data = json.loads(
            request.body
        )

        name = data.get(
            "name",
            ""
        ).strip()

        if not name:

            return JsonResponse({

                "status":
                    "error",

                "message":
                    "Category name required"

            })

        category, created = ProductCategory.objects.get_or_create(
            name=name
        )

        return JsonResponse({

            "status":
                "success",

            "id":
                category.id,

            "name":
                category.name

        })

    except Exception as e:

        return JsonResponse({

            "status":
                "error",

            "message":
                str(e)

        })



@login_required
def get_po_items(request):

    po_number = request.GET.get("po_number")

    try:

        po = PurchaseOrder.objects.prefetch_related(
            "items"
        ).get(
            po_number=po_number
        )

        items = []

        for item in po.items.all():

            ordered_qty = float(item.quantity)

            received_qty = float(
                item.received_quantity
            )

            balance_qty = (
                ordered_qty -
                received_qty
            )

            items.append({

                "item_id":
                    item.id,

                "code":
                    item.product_code,

                "product":
                    item.description,

                "ordered_qty":
                    ordered_qty,

                "received_qty":
                    received_qty,

                "balance_qty":
                    balance_qty,

                "rate":
                    float(item.rate)

            })

        return JsonResponse({

            "status":
                "success",

            "po_id":
                po.id,

            "po_number":
                po.po_number,

            "supplier":
                po.supplier_name,

            "po_status":
                po.status,

            "items":
                items

        })

    except PurchaseOrder.DoesNotExist:

        return JsonResponse({

            "status":
                "error",

            "message":
                "PO Not Found"

        })

    except Exception as e:

        return JsonResponse({

            "status":
                "error",

            "message":
                str(e)

        })






@login_required
@require_POST
def inward_po(request):

    try:

        data = json.loads(request.body)

        po = PurchaseOrder.objects.get(
            id=data["po_id"]
        )
        if po.status == "received":

            return JsonResponse({
                "status": "error",
                "message": f"PO {po.po_number} already fully received"
            })
        # =====================================================
        # IMAGE PROCESSING
        # =====================================================
        image_file = None

        if data.get("image"):

            try:

                format, imgstr = data["image"].split(";base64,")

                ext = format.split("/")[-1]

                image_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f"{uuid4()}.{ext}"
                )

            except Exception:
                image_file = None

        with transaction.atomic():

            current_year = timezone.now().year

            last_batch = GoodsBatch.objects.filter(
                batch_id__startswith=f"GRN{current_year}-"
            ).order_by("-batch_id").first()

            if last_batch:

                try:
                    last_no = int(
                        last_batch.batch_id.split("-")[1]
                    )
                except:
                    last_no = 0

                next_no = last_no + 1

            else:

                next_no = 1

            batch_id = (
                f"GRN{current_year}-"
                f"{str(next_no).zfill(4)}"
            )

            # =====================================================
            # CREATE GOODS BATCH
            # =====================================================
            local_now = timezone.localtime()
            batch = GoodsBatch.objects.create(
                batch_id=batch_id,
                po_reference=po.po_number,
                from_location=po.supplier_name,
                to_location="Main Store",
                transporter="",
                date=local_now.date(),
                time=local_now.time(),
                image=image_file,
                created_by=request.user,
                status="Confirmed",
                confirmed_by=request.user,
                confirmed_at=timezone.now()
            )

            total_lines = 0

            # =====================================================
            # PROCESS ITEMS
            # =====================================================
            for row in data.get("items", []):

                qty = Decimal(
                    str(row.get("received_qty", 0))
                )

                if qty <= 0:
                    continue

                po_item = PurchaseOrderItem.objects.get(
                    id=row.get("item_id")
                )
                # ==========================================
                # CATEGORY / PRODUCT MASTER
                # ==========================================

                category_id = row.get(
                    "category_id"
                )

                if not category_id:

                    raise Exception(
                        f"Category not selected for {po_item.product_code}"
                    )

                category = ProductCategory.objects.get(
                    id=category_id
                )

                product, created = Product.objects.get_or_create(

                    product_code=po_item.product_code,

                    defaults={

                        "product_name":
                            po_item.description,

                        "category":
                            category,

                        "unit":
                            po_item.unit,

                    }

                )

                # Existing product but category missing
                if product.category_id != category.id:

                    product.category = category
                    product.save()

                # Link PO Item
                if not po_item.product:

                    po_item.product = product
                    po_item.save()

                balance_qty = (
                    po_item.quantity -
                    po_item.received_quantity
                )

                # Prevent over receipt
                if qty > balance_qty:

                    raise Exception(
                        f"{po_item.product_code} balance quantity is only {balance_qty}"
                    )

                total_lines += 1

                # ==========================================
                # UPDATE PO RECEIVED QTY
                # ==========================================
                po_item.received_quantity += qty
                po_item.save()

                # ==========================================
                # CREATE GRN ITEM
                # ==========================================
                GoodsItem.objects.create(
                    batch=batch,
                    product=product,
                    product_code=po_item.product_code,
                    product_name=po_item.description,
                    quantity=qty,
                    price=po_item.rate
                )

                # ==========================================
                # UPDATE INVENTORY
                # ==========================================
                stock, created = Inventory.objects.get_or_create(
                    product_code=po_item.product_code,
                    defaults={
                        "product": product,
                        "product_name": po_item.description,
                        "stock_qty": Decimal("0")
                    }
                )

                stock.product = product
                stock.product_name = po_item.description
                stock.stock_qty += qty
                stock.save()

                # ==========================================
                # INVENTORY TRANSACTION
                # ==========================================
                InventoryTransaction.objects.create(
                    product_code=po_item.product_code,
                    product_name=po_item.description,
                    quantity=qty,
                    transaction_type="IN",
                    reference_no=po.po_number,
                    remarks=f"PO Inward - {po.po_number}",
                    created_by=request.user
                )

            # =====================================================
            # VALIDATION
            # =====================================================
            if total_lines == 0:

                transaction.set_rollback(True)

                return JsonResponse({
                    "status": "error",
                    "message": "No received quantity entered"
                })

            # =====================================================
            # UPDATE PO STATUS
            # =====================================================
            all_received = True

            for item in po.items.all():

                if item.received_quantity < item.quantity:

                    all_received = False
                    break

            if all_received:

                po.status = "received"

            else:

                po.status = "partial_received"

            po.save()

            # =====================================================
            # AUDIT LOG
            # =====================================================
            AuditLog.objects.create(
                user=request.user,
                module="Inventory",
                action="INWARD",
                object_id=po.po_number,
                ip_address=request.META.get(
                    "REMOTE_ADDR"
                ),
                description=(
                    f"PO {po.po_number} inwarded "
                    f"into inventory with Batch "
                    f"{batch_id}"
                )
            )

        return JsonResponse({
            "status": "success",
            "batch_id": batch_id,
            "message": (
                f"PO {po.po_number} inwarded successfully"
            )
        })

    except PurchaseOrder.DoesNotExist:

        return JsonResponse({
            "status": "error",
            "message": "Purchase Order not found"
        })

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)







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



from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum

from po_qu.models import PurchaseOrderItem

from .models import (
    MaterialIssue,
    Inventory,
    InventoryTransaction
)


@login_required
def inventory_dashboard(request):

    # =====================================================
    # PO SUMMARY
    # =====================================================

    rows = []

    total_products = 0

    total_ordered = Decimal("0")

    total_received = Decimal("0")

    total_balance = Decimal("0")

    po_items = PurchaseOrderItem.objects.select_related(
        "po"
    ).order_by(
        "-po__id",
        "id"
    )

    for item in po_items:

        balance_qty = (
            item.quantity -
            item.received_quantity
        )

        if balance_qty <= 0:

            status = "Complete"

        elif item.received_quantity > 0:

            status = "Partial"

        else:

            status = "Pending"

        rows.append({

            "po_number":
                item.po.po_number,

            "supplier":
                item.po.supplier_name,

            "product_code":
                item.product_code,

            "product_name":
                item.description,

            "ordered_qty":
                item.quantity,

            "received_qty":
                item.received_quantity,

            "balance_qty":
                balance_qty,

            "status":
                status,

        })

        total_products += 1

        total_ordered += item.quantity

        total_received += item.received_quantity

        total_balance += balance_qty

    # =====================================================
    # INVENTORY SUMMARY
    # =====================================================

    inventory_summary = []

    total_stock = Decimal("0")

    total_issued_stock = Decimal("0")

    for stock in Inventory.objects.all().order_by(
        "product_code"
    ):

        received_qty = (
            InventoryTransaction.objects.filter(
                product_code=stock.product_code,
                transaction_type="IN"
            ).aggregate(
                total=Sum("quantity")
            )["total"] or Decimal("0")
        )

        issued_qty = (
            InventoryTransaction.objects.filter(
                product_code=stock.product_code,
                transaction_type="OUT"
            ).aggregate(
                total=Sum("quantity")
            )["total"] or Decimal("0")
        )

        inventory_summary.append({
            
            "category":
                stock.product.category.name
                if stock.product and stock.product.category
                else "Uncategorized",

            "product_code":
                stock.product_code,

            "product_name":
                stock.product_name,

            "total_received":
                received_qty,

            "total_issued":
                issued_qty,

            "available_stock":
                stock.stock_qty,

        })

        total_stock += stock.stock_qty

        total_issued_stock += issued_qty


    # =====================================================
    # INVENTORY ITEMS FOR CATEGORY VIEW
    # =====================================================

    inventory_items = Inventory.objects.select_related(
        "product",
        "product__category"
    ).order_by(
        "product__category__name",
        "product_name"
    )
    # =====================================================
    # MATERIAL ISSUE HISTORY
    # =====================================================

    issued_materials = MaterialIssue.objects.select_related(
        "workorder_item",
        "workorder_item__work_order",
        "issued_by"
    ).order_by(
        "-issued_at"
    )

    # =====================================================
    # CONTEXT
    # =====================================================
    categories = ProductCategory.objects.all().order_by("name")
    context = {

        "rows":
            rows,

        "total_products":
            total_products,

        "total_ordered":
            total_ordered,

        "total_received":
            total_received,

        "total_balance":
            total_balance,

        "total_stock":
            total_stock,

        "total_issued_stock":
            total_issued_stock,

        "inventory_summary":
            inventory_summary,

        "inventory_items":
            inventory_items,

        "categories":
            categories,

        "issued_materials":
            issued_materials,

    }

    return render(
        request,
        "goods_entry/inventory_dashboard.html",
        context
    )

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@login_required
def inward_detail(request):

    po_number = request.GET.get("po_number")

    batches = GoodsBatch.objects.filter(
        po_reference=po_number
    ).prefetch_related("items")

    data = []

    for batch in batches:

        items = []

        for item in batch.items.all():

            items.append({
                "product_code": item.product_code,
                "product_name": item.product_name,
                "quantity": float(item.quantity),
                "price": float(item.price),
            })

        data.append({

            "batch_id": batch.batch_id,

            "po_number": batch.po_reference,

            "supplier": batch.from_location,

            "received_datetime": localtime(
                batch.created_at
            ).strftime("%d-%m-%Y %I:%M %p"),

            "status": batch.status,

            "confirmed_by": (
                str(batch.confirmed_by)
                if batch.confirmed_by
                else "-"
            ),

            "image": (
                batch.image.url
                if batch.image
                else ""
            ),

            "items": items

        })

    return JsonResponse({
        "status": "success",
        "batches": data
    })


@login_required
def material_issue_page(request):

    workorders = WorkOrder.objects.all().order_by(
        "-id"
    )

    return render(
        request,
        "goods_entry/material_issue.html",
        {
            "workorders": workorders
        }
    )


@login_required
def get_workorder_items(request):

    wo_id = request.GET.get("wo_id")

    try:

        workorder = WorkOrder.objects.prefetch_related(
            "items",
            "items__material_issues"
        ).get(
            id=wo_id
        )

        items = []

        for item in workorder.items.all():

            stock = Inventory.objects.filter(
                product_code=item.product_code
            ).first()

            available_qty = (
                float(stock.stock_qty)
                if stock else 0
            )

            issued_qty = sum(
                issue.issued_qty
                for issue in item.material_issues.all()
            )

            pending_qty = (
                item.quantity -
                issued_qty
            )

            # Skip fully issued items
            if pending_qty <= 0:

                continue

            items.append({

                "item_id":
                    item.id,

                "product_code":
                    item.product_code,

                "product_name":
                    item.product_name,

                "required_qty":
                    float(item.quantity),

                "issued_qty":
                    float(issued_qty),

                "pending_qty":
                    float(pending_qty),

                "available_qty":
                    available_qty

            })

        return JsonResponse({

            "status": "success",

            "wo_number":
                workorder.wo_number,

            "items":
                items

        })

    except WorkOrder.DoesNotExist:

        return JsonResponse({

            "status": "error",

            "message":
                "Work Order Not Found"

        })

    except Exception as e:

        return JsonResponse({

            "status": "error",

            "message":
                str(e)

        })




@login_required
@require_POST
def issue_material(request):

    try:

        data = json.loads(request.body)

        with transaction.atomic():

            total_issued = 0

            for row in data.get("items", []):

                issue_qty = Decimal(
                    str(
                        row.get(
                            "issue_qty",
                            0
                        )
                    )
                )

                if issue_qty <= 0:

                    continue

                # =====================================
                # WORK ORDER ITEM
                # =====================================

                workorder_item = WorkOrderItem.objects.get(
                    id=row.get("item_id")
                )

                # =====================================
                # INVENTORY CHECK
                # =====================================

                stock = Inventory.objects.get(
                    product_code=row.get(
                        "product_code"
                    )
                )

                if stock.stock_qty < issue_qty:

                    return JsonResponse({

                        "status": "error",

                        "message":
                            f"Insufficient stock for "
                            f"{stock.product_code}. "
                            f"Available: "
                            f"{stock.stock_qty}"

                    })

                # =====================================
                # DEDUCT STOCK
                # =====================================

                stock.stock_qty -= issue_qty

                stock.save()

                total_issued += issue_qty

                # =====================================
                # MATERIAL ISSUE ENTRY
                # =====================================

                MaterialIssue.objects.create(

                    workorder_item=
                        workorder_item,

                    product_code=
                        stock.product_code,

                    product_name=
                        stock.product_name,

                    issued_qty=
                        issue_qty,

                    issued_by=
                        request.user

                )

                # =====================================
                # INVENTORY TRANSACTION
                # =====================================

                InventoryTransaction.objects.create(

                    product_code=
                        stock.product_code,

                    product_name=
                        stock.product_name,

                    quantity=
                        issue_qty,

                    transaction_type=
                        "OUT",

                    reference_no=
                        workorder_item.work_order.wo_number,

                    remarks=
                        f"Material Issue - "
                        f"{workorder_item.work_order.wo_number}",

                    created_by=
                        request.user

                )

            if total_issued == 0:

                return JsonResponse({

                    "status": "error",

                    "message":
                        "No quantity entered"

                })

        return JsonResponse({

            "status": "success",

            "message":
                "Material issued successfully"

        })

    except Inventory.DoesNotExist:

        return JsonResponse({

            "status": "error",

            "message":
                "Inventory item not found"

        })

    except WorkOrderItem.DoesNotExist:

        return JsonResponse({

            "status": "error",

            "message":
                "Work Order Item not found"

        })

    except Exception as e:

        return JsonResponse({

            "status": "error",

            "message":
                str(e)

        }, status=400)
