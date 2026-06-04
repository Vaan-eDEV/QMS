from django.shortcuts import render, redirect, get_object_or_404
from .models import PurchaseOrder, PurchaseOrderItem
from django.contrib.auth.decorators import login_required
from .models import WorkOrder
from django.contrib import messages
from .models import (PurchaseOrder,PurchaseOrderItem,Quotation,QuotationItem,DeliveryChallan,DeliveryChallanItem,WorkOrder,WorkOrderItem,RFQ,RFQItem)
@login_required
def po_au_view(request):

    # =====================================================
    # PURCHASE ORDERS
    # =====================================================

    pos = (

        PurchaseOrder.objects

        .all()

        .order_by("-id")

    )

    # =====================================================
    # RFQ
    # =====================================================

    rfqs = (

        RFQ.objects

        .all()

        .order_by("-id")

    )

    # =====================================================
    # QUOTATIONS
    # =====================================================

    quotations = (

        Quotation.objects

        .all()

        .order_by("-id")

    )

    # =====================================================
    # DELIVERY CHALLANS
    # =====================================================

    dcs = (

        DeliveryChallan.objects

        .all()

        .order_by("-id")

    )

    # =====================================================
    # WORK ORDERS
    # =====================================================

    workorders = (

        WorkOrder.objects

        .prefetch_related("items")

        .all()

        .order_by("-id")

    )

    # =====================================================
    # PAGE
    # =====================================================

    return render(

        request,

        "po_qu/po_au.html",

        {

            # =================================================
            # DATA
            # =================================================

            "pos": pos,

            "rfqs": rfqs,

            "quotations": quotations,

            "dcs": dcs,

            "workorders": workorders,

            # =================================================
            # COUNTS
            # =================================================

            "total_po": pos.count(),

            "total_rfq": rfqs.count(),

            "total_quotation": quotations.count(),

            "total_dc": dcs.count(),

            "total_workorders": workorders.count(),

        }

    )

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.db import transaction
from decimal import Decimal
from django.contrib.auth.decorators import login_required

from .models import PurchaseOrder, PurchaseOrderItem


# ================= CREATE PO =================
@login_required
def create_po(request):

    if request.method == "POST":

        po = PurchaseOrder.objects.create(
            reference=request.POST.get("reference"),
            date=request.POST.get("date"),

            supplier_name=request.POST.get("supplier_name"),
            supplier_address=request.POST.get("supplier_address"),
            supplier_phone=request.POST.get("supplier_phone"),
            supplier_gstin=request.POST.get("supplier_gstin"),

            billing_name=request.POST.get("billing_name"),
            billing_address=request.POST.get("billing_address"),
            billing_phone=request.POST.get("billing_phone"),
            billing_gstin=request.POST.get("billing_gstin"),

            shipping_name=request.POST.get("shipping_name"),
            shipping_address=request.POST.get("shipping_address"),
            shipping_phone=request.POST.get("shipping_phone"),
            shipping_gstin=request.POST.get("shipping_gstin"),

            discount_percentage=Decimal(request.POST.get("discount") or 0),
            cgst_percentage=Decimal(request.POST.get("cgst") or 0),
            sgst_percentage=Decimal(request.POST.get("sgst") or 0),
            igst_percentage=Decimal(request.POST.get("igst") or 0),

            note=request.POST.get("note") or "",
            terms=request.POST.get("terms") or "",
        )

        # 🔹 Items
        codes = request.POST.getlist('product_code[]')
        descs = request.POST.getlist('description[]')
        units = request.POST.getlist('unit[]')
        qtys = request.POST.getlist('quantity[]')
        rates = request.POST.getlist('rate[]')

        for code, desc, unit, qty, rate in zip(codes, descs, units, qtys, rates):
            if code:
                qty = float(qty or 0)
                rate = float(rate or 0)

                PurchaseOrderItem.objects.create(
                    po=po,
                    product_code=code,
                    description=desc,
                    unit=unit,
                    quantity=qty,
                    rate=rate,
                    amount=qty * rate   # ✅ FIXED
                )

        # 🔥 Calculate totals
        po.calculate_totals()
        po.save()

        return redirect('po_qu:po_detail', po_id=po.id)

    return render(request, "po_qu/po/create_po.html")


# ================= EDIT PO =================
@login_required
def edit_po(request, po_id):

    po = get_object_or_404(PurchaseOrder, id=po_id)

    # 🔒 Prevent editing after approval
    if po.approved_by:
        return HttpResponse("Cannot edit approved PO", status=403)

    if request.method == "POST":

        po.reference = request.POST.get("reference")
        po.date = request.POST.get("date")

        po.supplier_name = request.POST.get("supplier_name")
        po.supplier_address = request.POST.get("supplier_address")
        po.supplier_phone = request.POST.get("supplier_phone")
        po.supplier_gstin = request.POST.get("supplier_gstin")

        po.billing_name = request.POST.get("billing_name")
        po.billing_address = request.POST.get("billing_address")
        po.billing_phone = request.POST.get("billing_phone")
        po.billing_gstin = request.POST.get("billing_gstin")

        po.shipping_name = request.POST.get("shipping_name")
        po.shipping_address = request.POST.get("shipping_address")
        po.shipping_phone = request.POST.get("shipping_phone")
        po.shipping_gstin = request.POST.get("shipping_gstin")

        po.note = request.POST.get("note")
        po.terms = request.POST.get("terms")

        codes = request.POST.getlist("product_code[]")
        descs = request.POST.getlist("description[]")
        units = request.POST.getlist("unit[]")
        qtys = request.POST.getlist("quantity[]")
        rates = request.POST.getlist("rate[]")

        with transaction.atomic():

            po.save()
            po.items.all().delete()

            for code, desc, unit, qty, rate in zip(codes, descs, units, qtys, rates):
                if code:
                    qty = float(qty or 0)
                    rate = float(rate or 0)

                    PurchaseOrderItem.objects.create(
                        po=po,
                        product_code=code,
                        description=desc,
                        unit=unit,
                        quantity=qty,
                        rate=rate,
                        amount=qty * rate
                    )

            # 🔥 MAIN FIX (VERY IMPORTANT)
            po.calculate_totals()
            po.save()

        return redirect("po_qu:po_detail", po_id=po.id)

    return render(request, "po_qu/po/create_po.html", {
        "po": po,
        "edit_mode": True
    })
def po_detail(request, po_id):
    po = get_object_or_404(PurchaseOrder, id=po_id)
    return render(request, "po_qu/po/po_detail.html", {"po": po})


def po_list(request):
    pos = PurchaseOrder.objects.all().order_by('-id')
    return render(request, 'po_qu/po/po_list.html', {'pos': pos})


from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from django.conf import settings
import os

def generate_po_pdf(request, po_id):

    po = PurchaseOrder.objects.get(id=po_id)

    # 🔒 Allow only after approval
    if not po.prepared_by or not po.approved_by:
        return HttpResponse("Not allowed", status=403)

    template = get_template("po_qu/po/po_pdf.html")

    html = template.render({
        "po": po,
        "logo_path": request.build_absolute_uri("/static/img/logo.jpeg"),
        "qr_code_path": po.qr_code.url if po.qr_code else "",
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=PO_{po.id}.pdf'

    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)

    return response
# ======================================== Quotation =================================================


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from .models import Quotation, QuotationItem


# =====================================
# CREATE QUOTATION
# =====================================
# @login_required
# def create_quotation(request):

#     if request.method == "POST":

#         quotation = Quotation(
#             date=request.POST.get("date"),
#             valid_till=request.POST.get("valid_till"),
#             reference=request.POST.get("reference"),
#             subject=request.POST.get("subject"),

#             customer_name=request.POST.get("customer_name"),
#             customer_email=request.POST.get("customer_email"),
#             customer_phone=request.POST.get("customer_phone"),
#             customer_address=request.POST.get("customer_address"),
#             customer_gstin=request.POST.get("customer_gstin"),

#             discount_percentage=Decimal(request.POST.get("discount", 0) or 0),
#             cgst_percentage=Decimal(request.POST.get("cgst", 0) or 0),
#             sgst_percentage=Decimal(request.POST.get("sgst", 0) or 0),
#             igst_percentage=Decimal(request.POST.get("igst", 0) or 0),

#             note=request.POST.get("note") or "",
#             terms=request.POST.get("terms") or "",

#             created_by=request.user
#         )

#         quotation.save()

#         # 🔹 Items
#         descriptions = request.POST.getlist('description[]')
#         hsn_codes = request.POST.getlist('hsn_code[]')
#         quantities = request.POST.getlist('quantity[]')
#         units = request.POST.getlist('unit[]')
#         rates = request.POST.getlist('rate[]')

#         for i in range(len(descriptions)):
#             if descriptions[i]:
#                 QuotationItem.objects.create(
#                     quotation=quotation,
#                     description=descriptions[i],
#                     hsn_code=hsn_codes[i],
#                     quantity=Decimal(quantities[i] or 0),
#                     unit=units[i],
#                     rate=Decimal(rates[i] or 0),
#                 )

#         # 🔥 Recalculate totals after items added
#         quotation.calculate_totals()
#         quotation.save()

#         return redirect('po_qu:quotation_detail', quotation_id=quotation.id)

#     return render(request, "po_qu/quotation/create_quotation.html")

from form_builder.models import FormResponse
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def create_quotation(request):

    selected_ref = request.GET.get("ref_id")
    selected_company = request.GET.get("company")

    # ================= DROPDOWN =================
    rfq_list = (
        FormResponse.objects
        .filter(form__process="COSTING",is_costing_approved=True)
        .exclude(ref_id__isnull=True)
        .exclude(company__isnull=True)
        .values("ref_id", "company")
        .distinct()
    )

    # ================= PREFILL =================
    prefill = {
        "reference": selected_ref or "",
        "subject": "",
        "customer_name": selected_company or "",
        "customer_email": "",
        "customer_phone": "",
        "customer_address": "",
        "customer_gstin": "",
        "items": []
    }

    # ================= LOAD COSTING =================
    if selected_ref and selected_company:

        responses = FormResponse.objects.filter(
            ref_id=selected_ref,
            company=selected_company,
            form__process="COSTING",
            is_costing_approved=True
        )

        for res in responses:

            data = res.data or {}

            # ================= FIELD MAPPING =================
            for key, value in data.items():

                key_clean = key.lower().strip()

                if key_clean in ["subject"]:
                    prefill["subject"] = value

                elif key_clean in ["customer name", "customer_name"]:
                    prefill["customer_name"] = value

                elif key_clean in ["email", "customer_email"]:
                    prefill["customer_email"] = value

                elif key_clean in ["phone", "customer_phone"]:
                    prefill["customer_phone"] = value

                elif key_clean in ["address", "customer_address"]:
                    prefill["customer_address"] = value

                elif key_clean in ["gstin", "customer_gstin"]:
                    prefill["customer_gstin"] = value

                # ================= TABLE MAPPING =================
                elif isinstance(value, list):

                    for row in value:

                        # 🔥 HANDLE YOUR EXACT COLUMNS
                        part_id = (
                            row.get("Part Id") or
                            row.get("part_id") or
                            row.get("PartID") or
                            ""
                        )

                        part_name = (
                            row.get("Part Name") or
                            row.get("name") or
                            row.get("part_name") or
                            ""
                        )

                        # optional columns
                        qty = (
                            row.get("quantity") or
                            row.get("qty") or
                            row.get("a") or
                            0
                        )

                        rate = (
                            row.get("rate") or
                            row.get("b") or
                            0
                        )

                        # only push valid rows
                        if part_id or part_name:
                            prefill["items"].append({
                                "part_id": part_id,
                                "part_name": part_name,
                                "quantity": qty,
                                "unit": row.get("unit") or "",
                                "rate": rate,
                            })

    # ================= SAVE =================
    if request.method == "POST":

        quotation = Quotation(
            date=request.POST.get("date") or None,
            valid_till=request.POST.get("valid_till") or None,
            reference=request.POST.get("reference"),
            rfq_id=request.POST.get("reference"),   # 🔥 ADD THIS
            company=request.POST.get("customer_name"),
            subject=request.POST.get("subject"),

            customer_name=request.POST.get("customer_name"),
            customer_email=request.POST.get("customer_email"),
            customer_phone=request.POST.get("customer_phone"),
            customer_address=request.POST.get("customer_address"),
            customer_gstin=request.POST.get("customer_gstin"),

            discount_percentage=Decimal(request.POST.get("discount", 0) or 0),
            cgst_percentage=Decimal(request.POST.get("cgst", 0) or 0),
            sgst_percentage=Decimal(request.POST.get("sgst", 0) or 0),
            igst_percentage=Decimal(request.POST.get("igst", 0) or 0),

            note=request.POST.get("note") or "",
            terms=request.POST.get("terms") or "",

            created_by=request.user
        )

        quotation.save()

        part_id = request.POST.getlist('part_id[]')
        part_name = request.POST.getlist('part_name[]')
        quantities = request.POST.getlist('quantity[]')
        units = request.POST.getlist('unit[]')
        rates = request.POST.getlist('rate[]')

        for i in range(len(part_id)):
            if part_id[i]:
                QuotationItem.objects.create(
                    quotation=quotation,
                    part_id=part_id[i],
                    part_name=part_name[i],
                    quantity=Decimal(quantities[i] or 0),
                    unit=units[i],
                    rate=Decimal(rates[i] or 0),
                )

        quotation.calculate_totals()
        quotation.save()

        return redirect('po_qu:quotation_detail', quotation_id=quotation.id)

    return render(request, "po_qu/quotation/create_quotation.html", {
        "rfq_list": rfq_list,
        "prefill": prefill,
        "selected_ref": selected_ref,
        "selected_company": selected_company
    })

























from django.db import transaction

@login_required
def edit_quotation(request, quotation_id):

    quotation = get_object_or_404(Quotation, id=quotation_id)

    # 🔒 prevent edit after approval (optional)
    if quotation.approved_by:
        return HttpResponse("Cannot edit approved quotation", status=403)

    if request.method == "POST":

        quotation.date = ( request.POST.get("date") or None )
        quotation.valid_till = ( request.POST.get("valid_till") or None )
        quotation.reference = request.POST.get("reference")
        quotation.subject = request.POST.get("subject")

        quotation.customer_name = request.POST.get("customer_name")
        quotation.customer_email = request.POST.get("customer_email")
        quotation.customer_phone = request.POST.get("customer_phone")
        quotation.customer_address = request.POST.get("customer_address")
        quotation.customer_gstin = request.POST.get("customer_gstin")

        quotation.discount_percentage = Decimal(request.POST.get("discount") or 0)
        quotation.cgst_percentage = Decimal(request.POST.get("cgst") or 0)
        quotation.sgst_percentage = Decimal(request.POST.get("sgst") or 0)
        quotation.igst_percentage = Decimal(request.POST.get("igst") or 0)

        quotation.note = request.POST.get("note") or ""
        quotation.terms = request.POST.get("terms") or ""

        descriptions = request.POST.getlist('description[]')
        hsn_codes = request.POST.getlist('hsn_code[]')
        quantities = request.POST.getlist('quantity[]')
        units = request.POST.getlist('unit[]')
        rates = request.POST.getlist('rate[]')

        with transaction.atomic():

            quotation.save()
            quotation.items.all().delete()

            for desc, hsn, qty, unit, rate in zip(descriptions, hsn_codes, quantities, units, rates):
                if desc:
                    qty = Decimal(qty or 0)
                    rate = Decimal(rate or 0)

                    QuotationItem.objects.create(
                        quotation=quotation,
                        description=desc,
                        hsn_code=hsn,
                        quantity=qty,
                        unit=unit,
                        rate=rate,
                        amount=qty * rate
                    )

            # 🔥 IMPORTANT
            quotation.calculate_totals()
            quotation.save()

        return redirect('po_qu:quotation_detail', quotation_id=quotation.id)

    return render(request, "po_qu/quotation/create_quotation.html", {
        "quotation": quotation,
        "edit_mode": True
    })
# =====================================
# QUOTATION DETAIL
# =====================================
@login_required
def quotation_detail(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    return render(request, "po_qu/quotation/quotation_detail.html", {"quotation": quotation})


# =====================================
# QUOTATION LIST
# =====================================
@login_required
def quotation_list(request):
    quotations = Quotation.objects.all().order_by('-id')
    return render(request, "po_qu/quotation/quotation_list.html", {"quotations": quotations})



from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from django.shortcuts import get_object_or_404

from .models import Quotation


def generate_quotation_pdf(request, quotation_id):

    quotation = get_object_or_404(Quotation, id=quotation_id)

    # 🔒 Optional restriction (same like PO)
    if not quotation.prepared_by or not quotation.approved_by:
        return HttpResponse("Not allowed", status=403)

    template = get_template("po_qu/quotation/quotation_pdf.html")

    html = template.render({
        "quotation": quotation,
        "items": quotation.items.all(),

        "logo_path": request.build_absolute_uri("/static/img/logo.jpeg"),
        
        

        "qr_code_path": quotation.qr_code.url if hasattr(quotation, 'qr_code') and quotation.qr_code else "",

        "company_address": "Your Company Address",
        "company_phone": "9876543210",
        "company_email": "your@email.com",
    })

    response = HttpResponse(content_type='application/pdf')

    # 🔥 force download
    response['Content-Disposition'] = f'attachment; filename=Quotation_{quotation.id}.pdf'

    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)

    return response
#===================================================DC ==================================================================


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DeliveryChallan, DeliveryChallanItem


# ================= CREATE =================
@login_required
def create_dc(request):

    if request.method == "POST":

        dc = DeliveryChallan.objects.create(
            date=request.POST.get("date"),
            transporter=request.POST.get("transporter"),
            city=request.POST.get("city"),

            from_name=request.POST.get("from_name"),
            from_address=request.POST.get("from_address"),
            from_city=request.POST.get("from_city"),
            from_state=request.POST.get("from_state"),
            from_pincode=request.POST.get("from_pincode"),
            from_country=request.POST.get("from_country"),
            from_phone=request.POST.get("from_phone"),
            from_email=request.POST.get("from_email"),

            to_name=request.POST.get("to_name"),
            to_address=request.POST.get("to_address"),
            to_city=request.POST.get("to_city"),
            to_state=request.POST.get("to_state"),
            to_pincode=request.POST.get("to_pincode"),
            to_country=request.POST.get("to_country"),
            to_phone=request.POST.get("to_phone"),
            to_email=request.POST.get("to_email"),

            note=request.POST.get("note") or "",
            created_by=request.user
        )

        # ITEMS
        products = request.POST.getlist("product_name[]")
        units = request.POST.getlist("unit[]")
        quantities = request.POST.getlist("quantity[]")

        for i in range(len(products)):
            if products[i]:
                DeliveryChallanItem.objects.create(
                    dc=dc,
                    product_name=products[i],
                    unit=units[i],
                    quantity=quantities[i]
                )

        return redirect('po_qu:dc_detail', dc_id=dc.id)

    return render(request, "po_qu/dc/create_dc.html")

from django.db import transaction

@login_required
def edit_dc(request, dc_id):

    dc = get_object_or_404(DeliveryChallan, id=dc_id)

    # 🔒 prevent edit after approval (optional)
    if dc.approved_by:
        return HttpResponse("Cannot edit approved DC", status=403)

    if request.method == "POST":

        dc.date = request.POST.get("date")
        dc.transporter = request.POST.get("transporter")
        dc.city = request.POST.get("city")

        dc.from_name = request.POST.get("from_name")
        dc.from_address = request.POST.get("from_address")
        dc.from_city = request.POST.get("from_city")
        dc.from_state = request.POST.get("from_state")
        dc.from_pincode = request.POST.get("from_pincode")
        dc.from_country = request.POST.get("from_country")
        dc.from_phone = request.POST.get("from_phone")
        dc.from_email = request.POST.get("from_email")

        dc.to_name = request.POST.get("to_name")
        dc.to_address = request.POST.get("to_address")
        dc.to_city = request.POST.get("to_city")
        dc.to_state = request.POST.get("to_state")
        dc.to_pincode = request.POST.get("to_pincode")
        dc.to_country = request.POST.get("to_country")
        dc.to_phone = request.POST.get("to_phone")
        dc.to_email = request.POST.get("to_email")

        dc.note = request.POST.get("note") or ""

        products = request.POST.getlist("product_name[]")
        units = request.POST.getlist("unit[]")
        quantities = request.POST.getlist("quantity[]")

        with transaction.atomic():

            dc.save()
            dc.items.all().delete()

            for p, u, q in zip(products, units, quantities):
                if p:
                    DeliveryChallanItem.objects.create(
                        dc=dc,
                        product_name=p,
                        unit=u,
                        quantity=q
                    )

        return redirect('po_qu:dc_detail', dc_id=dc.id)

    return render(request, "po_qu/dc/create_dc.html", {
        "dc": dc,
        "edit_mode": True
    })
# ================= DETAIL =================
@login_required
def dc_detail(request, dc_id):
    dc = get_object_or_404(DeliveryChallan, id=dc_id)
    return render(request, "po_qu/dc/dc_detail.html", {"dc": dc})


# ================= LIST =================
@login_required
def dc_list(request):
    dcs = DeliveryChallan.objects.all().order_by('-id')
    return render(request, "po_qu/dc/dc_list.html", {"dcs": dcs})

from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from django.shortcuts import get_object_or_404

from .models import DeliveryChallan


def generate_dc_pdf(request, dc_id):

    dc = get_object_or_404(DeliveryChallan, id=dc_id)

    # 🔒 same restriction
    if not dc.prepared_by or not dc.approved_by:
        return HttpResponse("Not allowed", status=403)

    template = get_template("po_qu/dc/dc_pdf.html")

    html = template.render({
        "dc": dc,

        # ✅ EXACT SAME METHOD AS QUOTATION (this is key)
        "logo_path": request.build_absolute_uri("/static/img/logo.jpeg"),

        "qr_code_path": dc.qr_code.url if hasattr(dc, 'qr_code') and dc.qr_code else "",

        "company_address": "Your Company Address",
    })

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = f'attachment; filename=DC_{dc.id}.pdf'

    # ✅ same base_url
    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)

    return response




import uuid
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# @login_required
# def apply_signature(request):

#     if request.method != "POST":
#         return JsonResponse({"status": "error", "msg": "Invalid request"})

#     doc_type = request.POST.get("type")
#     doc_id = request.POST.get("id")
#     password = request.POST.get("password")
#     action = request.POST.get("action")

#     # ✅ BEST AUTH METHOD (works with custom user)
#     if not request.user.check_password(password):
#         return JsonResponse({"status": "error", "msg": "Wrong password"})


#     # 🔹 GET OBJECT
#     if doc_type == "po":

#         obj = PurchaseOrder.objects.get(id=doc_id)

#     elif doc_type == "quotation":

#         obj = Quotation.objects.get(id=doc_id)

#     elif doc_type == "workorder":

#         obj = WorkOrder.objects.get(id=doc_id)

#     else:

#         obj = DeliveryChallan.objects.get(id=doc_id)


#     signature_id = str(uuid.uuid4())[:12].upper()

#     # ================= PREPARE =================
#     if action == "prepare":

#         if obj.prepared_by:
#             return JsonResponse({"status": "error", "msg": "Already prepared"})

#         obj.prepared_by = request.user
#         obj.prepared_at = timezone.now()
#         obj.prepared_signature_id = f"PR-{signature_id}"

#     # ================= APPROVE =================
#     elif action == "approve":

#         if not obj.prepared_by:
#             return JsonResponse({"status": "error", "msg": "Prepare first"})

#         if obj.approved_by:
#             return JsonResponse({"status": "error", "msg": "Already approved"})

#         obj.approved_by = request.user
#         obj.approved_at = timezone.now()
#         obj.approved_signature_id = f"AP-{signature_id}"

#     else:
#         return JsonResponse({"status": "error", "msg": "Invalid action"})

#     # 🔥 GLOBAL DIGITAL ID (ONLY ONCE)
#     if not obj.digital_id:
#         obj.digital_id = f"DOC-{str(uuid.uuid4())[:10].upper()}"

#     obj.save()

#     return JsonResponse({"status": "success"})

@login_required
def apply_signature(request):

    # =====================================================
    # VALIDATE REQUEST
    # =====================================================

    if request.method != "POST":

        return JsonResponse({

            "status": "error",

            "msg": "Invalid request"

        })

    # =====================================================
    # REQUEST DATA
    # =====================================================

    doc_type = request.POST.get("type")

    doc_id = request.POST.get("id")

    password = request.POST.get("password")

    action = request.POST.get("action")

    # =====================================================
    # PASSWORD CHECK
    # =====================================================

    if not request.user.check_password(password):

        return JsonResponse({

            "status": "error",

            "msg": "Wrong password"

        })

    # =====================================================
    # GET DOCUMENT
    # =====================================================

    try:

        if doc_type == "po":

            obj = PurchaseOrder.objects.get(
                id=doc_id
            )

        elif doc_type == "quotation":

            obj = Quotation.objects.get(
                id=doc_id
            )

        elif doc_type == "wo":

            obj = WorkOrder.objects.get(
                id=doc_id
            )

        elif doc_type == "dc":

            obj = DeliveryChallan.objects.get(
                id=doc_id
            )

        elif doc_type == "rfq":

            obj = RFQ.objects.get(
                id=doc_id
            )

        else:

            return JsonResponse({

                "status": "error",

                "msg": "Invalid document type"

            })

    except Exception as e:

        return JsonResponse({

            "status": "error",

            "msg": str(e)

        })

    # =====================================================
    # GENERATE SIGNATURE ID
    # =====================================================

    signature_id = (

        str(uuid.uuid4())[:12]

        .upper()

    )

    # =====================================================
    # PREPARE
    # =====================================================

    if action == "prepare":

        # ---------------------------------------------
        # ALREADY PREPARED
        # ---------------------------------------------

        if obj.prepared_by:

            return JsonResponse({

                "status": "error",

                "msg": "Already prepared"

            })

        # ---------------------------------------------
        # SAVE PREPARE
        # ---------------------------------------------

        obj.prepared_by = request.user

        obj.prepared_at = timezone.now()

        obj.prepared_signature_id = (

            f"PR-{signature_id}"

        )

        # ---------------------------------------------
        # STATUS
        # ---------------------------------------------

        if hasattr(obj, "status"):

            obj.status = "prepared"

    # =====================================================
    # REVIEW
    # =====================================================

    elif action == "review":

        # ---------------------------------------------
        # MUST PREPARE FIRST
        # ---------------------------------------------

        if not obj.prepared_by:

            return JsonResponse({

                "status": "error",

                "msg": "Prepare first"

            })

        # ---------------------------------------------
        # ALREADY REVIEWED
        # ---------------------------------------------

        if obj.reviewed_by:

            return JsonResponse({

                "status": "error",

                "msg": "Already reviewed"

            })

        # ---------------------------------------------
        # SAVE REVIEW
        # ---------------------------------------------

        obj.reviewed_by = request.user

        obj.reviewed_at = timezone.now()

        obj.reviewed_signature_id = (

            f"RV-{signature_id}"

        )

        # ---------------------------------------------
        # STATUS
        # ---------------------------------------------

        if hasattr(obj, "status"):

            obj.status = "reviewed"

    # =====================================================
    # APPROVE
    # =====================================================

    elif action == "approve":

        # ---------------------------------------------
        # MUST REVIEW FIRST
        # ---------------------------------------------

        if not obj.reviewed_by:

            return JsonResponse({

                "status": "error",

                "msg": "Review first"

            })

        # ---------------------------------------------
        # ALREADY APPROVED
        # ---------------------------------------------

        if obj.approved_by:

            return JsonResponse({

                "status": "error",

                "msg": "Already approved"

            })

        # ---------------------------------------------
        # SAVE APPROVAL
        # ---------------------------------------------

        obj.approved_by = request.user

        obj.approved_at = timezone.now()

        obj.approved_signature_id = (

            f"AP-{signature_id}"

        )

        # ---------------------------------------------
        # STATUS
        # ---------------------------------------------

        if hasattr(obj, "status"):

            obj.status = "approved"

    # =====================================================
    # INVALID ACTION
    # =====================================================

    else:

        return JsonResponse({

            "status": "error",

            "msg": "Invalid action"

        })

    # =====================================================
    # GLOBAL DIGITAL DOCUMENT ID
    # =====================================================

    if not obj.digital_id:

        obj.digital_id = (

            f"DOC-"

            f"{str(uuid.uuid4())[:10].upper()}"

        )

    # =====================================================
    # SAVE
    # =====================================================

    obj.save()

    # =====================================================
    # RESPONSE
    # =====================================================

    return JsonResponse({

        "status": "success",

        "msg": "Signature applied successfully",

        "prepared_by": (

            str(obj.prepared_by)

            if obj.prepared_by else ""

        ),

        "reviewed_by": (

            str(obj.reviewed_by)

            if obj.reviewed_by else ""

        ),

        "approved_by": (

            str(obj.approved_by)

            if obj.approved_by else ""

        ),

        "digital_id": obj.digital_id,

        "document_status": (

            obj.status

            if hasattr(obj, "status")

            else ""

        )

    })






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import transaction
from django.template.loader import get_template
from weasyprint import HTML
from .models import WorkOrder, WorkOrderItem, WorkOrderDelivery
from form_builder.models import FormResponse


# ==========================================================
# 🔷 LIST
@login_required
def workorder_list(request):

    workorders = (
        WorkOrder.objects
        .all()
        .order_by("-created_at")
    )

    total_workorders = workorders.count()

    draft_count = workorders.filter(
        status="draft"
    ).count()

    approved_count = workorders.filter(
        status="approved"
    ).count()

    prepared_count = workorders.filter(
        status="prepared"
    ).count()

    return render(
        request,
        "po_qu/workorder/workorder_list.html",
        {
            "workorders": workorders,

            "total_workorders": total_workorders,

            "draft_count": draft_count,

            "approved_count": approved_count,

            "prepared_count": prepared_count,
        }
    )

# ==========================================================
# 🔷 DETAIL
# ==========================================================
# ==========================================================
# 🔷 WORKORDER DETAIL
# ==========================================================

@login_required
def workorder_detail(request, wo_id):

    wo = get_object_or_404(
        WorkOrder,
        id=wo_id
    )

    items = (
        wo.items
        .all()
        .prefetch_related("deliveries")
    )

    total_items = items.count()

    total_quantity = sum(
        item.quantity for item in items
    )

    completed_deliveries = sum(
        item.deliveries.count()
        for item in items
    )

    return render(

        request,

        "po_qu/workorder/workorder_detail.html",

        {

            "wo": wo,

            "items": items,

            "total_items": total_items,

            "total_quantity": total_quantity,

            "completed_deliveries": completed_deliveries,

        }

    )


# ==========================================================
# 🔷 CREATE (AUTO-FILL)
# ==========================================================
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def create_workorder(request):

    selected_ref = request.GET.get("ref_id")

    selected_company = request.GET.get("company")

    # =====================================================
    # RFQ DROPDOWN
    # =====================================================

    rfq_list = (

        FormResponse.objects

        .filter(
            form__process="COSTING",
            is_costing_approved=True
        )

        .exclude(ref_id__isnull=True)

        .exclude(company__isnull=True)

        .values("ref_id", "company")

        .distinct()

    )

    # =====================================================
    # PREFILL
    # =====================================================

    prefill = {

        "po_number": selected_ref or "",

        "customer_name": selected_company or "",

        "customer_address": "",

        "items": []

    }

    # =====================================================
    # AUTO LOAD COSTING DATA
    # =====================================================

    if selected_ref and selected_company:

        responses = FormResponse.objects.filter(

            ref_id=selected_ref,

            company=selected_company,

            form__process="COSTING",

            is_costing_approved=True

        )

        for res in responses:

            data = res.data or {}

            for key, value in data.items():

                key_clean = key.lower().strip()

                # =================================================
                # CUSTOMER DETAILS
                # =================================================

                if key_clean in [
                    "customer name",
                    "company"
                ]:

                    prefill["customer_name"] = value

                elif key_clean in [
                    "address",
                    "customer_address"
                ]:

                    prefill["customer_address"] = value

                # =================================================
                # TABLE ITEMS
                # =================================================

                elif isinstance(value, list):

                    for row in value:

                        part_id = (

                            row.get("Part Id")

                            or row.get("part_id")

                            or row.get("PartID")

                            or ""

                        )

                        part_name = (

                            row.get("Part Name")

                            or row.get("name")

                            or row.get("part_name")

                            or ""

                        )

                        qty = (

                            row.get("quantity")

                            or row.get("qty")

                            or 0

                        )

                        material = row.get("material") or ""

                        unit = row.get("unit") or "Nos"

                        if part_id or part_name:

                            prefill["items"].append({

                                "product_code": part_id,

                                "product_name": part_name,

                                "material": material,

                                "quantity": qty,

                                "unit": unit,

                                "deliveries": []

                            })

    # =====================================================
    # SAVE WORKORDER
    # =====================================================

    if request.method == "POST":

        with transaction.atomic():

            # =================================================
            # CREATE HEADER
            # =================================================

            wo = WorkOrder.objects.create(

                rfq_ref=selected_ref,

                date=request.POST.get("date"),

                customer_name=request.POST.get(
                    "customer_name"
                ),

                customer_address=request.POST.get(
                    "customer_address"
                ),

                po_number=request.POST.get(
                    "po_number"
                ),

                po_date=request.POST.get(
                    "po_date"
                ) or None,

                product_notes=request.POST.get(
                    "product_notes"
                ) or "",

                process_notes=request.POST.get(
                    "process_notes"
                ) or "",

                packing_notes=request.POST.get(
                    "packing_notes"
                ) or "",

                delivery_notes=request.POST.get(
                    "delivery_notes"
                ) or "",

                documentation_notes=request.POST.get(
                    "documentation_notes"
                ) or "",

                other_notes=request.POST.get(
                    "other_notes"
                ) or "",

                created_by=request.user

            )

            # =================================================
            # ITEM DATA
            # =================================================

            product_codes = request.POST.getlist(
                "product_code[]"
            )

            product_names = request.POST.getlist(
                "product_name[]"
            )

            materials = request.POST.getlist(
                "material[]"
            )

            quantities = request.POST.getlist(
                "quantity[]"
            )

            units = request.POST.getlist(
                "unit[]"
            )

            assigned_users = request.POST.getlist(
                "assigned_to[]"
            )

            # =================================================
            # CREATE ITEMS
            # =================================================

            for i in range(len(product_codes)):

                if not product_codes[i]:
                    continue

                assigned_user = None

                if i < len(assigned_users):

                    user_id = assigned_users[i]

                    if user_id:

                        try:

                            assigned_user = User.objects.get(
                                id=user_id
                            )

                        except User.DoesNotExist:

                            assigned_user = None

                # =============================================
                # CREATE ITEM
                # =============================================

                item = WorkOrderItem.objects.create(

                    work_order=wo,

                    product_code=product_codes[i],

                    product_name=product_names[i],

                    material=materials[i],

                    quantity=int(
                        quantities[i] or 0
                    ),

                    unit=units[i],

                    status="INTERNAL_WORKORDER",

                    assigned_to=assigned_user

                )

                # =============================================
                # DELIVERY SCHEDULE
                # =============================================

                dates = request.POST.getlist(
                    f"delivery_date_{i}[]"
                )

                qtys = request.POST.getlist(
                    f"delivery_qty_{i}[]"
                )

                for d, q in zip(dates, qtys):

                    if d:

                        WorkOrderDelivery.objects.create(

                            item=item,

                            delivery_date=d,

                            quantity=int(q or 0)

                        )

        return redirect(

            "po_qu:workorder_detail",

            wo_id=wo.id

        )

    # =====================================================
    # PAGE
    # =====================================================

    users = User.objects.filter(
        is_active=True
    ).order_by("email")

    return render(

        request,

        "po_qu/workorder/create_workorder.html",

        {

            "rfq_list": rfq_list,

            "prefill": prefill,

            "selected_ref": selected_ref,

            "selected_company": selected_company,

            "users": users

        }

    )
# ==========================================================
# 🔷 EDIT
# ==========================================================

@login_required
def edit_workorder(request, wo_id):

    wo = get_object_or_404(WorkOrder, id=wo_id)

    if request.method == "POST":

        with transaction.atomic():

            wo.date = request.POST.get("date")
            wo.customer_name = request.POST.get("customer_name")
            wo.customer_address = request.POST.get("customer_address")

            wo.po_number = request.POST.get("po_number")
            wo.po_date = request.POST.get("po_date") or None

            wo.product_notes = request.POST.get("product_notes") or ""
            wo.process_notes = request.POST.get("process_notes") or ""
            wo.packing_notes = request.POST.get("packing_notes") or ""
            wo.delivery_notes = request.POST.get("delivery_notes") or ""
            wo.documentation_notes = request.POST.get("documentation_notes") or ""
            wo.other_notes = request.POST.get("other_notes") or ""

            wo.save()

            # 🔥 RESET ITEMS
            wo.items.all().delete()

            product_codes = request.POST.getlist("product_code[]")
            product_names = request.POST.getlist("product_name[]")
            materials = request.POST.getlist("material[]")
            quantities = request.POST.getlist("quantity[]")
            units = request.POST.getlist("unit[]")

            for i in range(len(product_codes)):

                if not product_codes[i]:
                    continue

                item = WorkOrderItem.objects.create(
                    work_order=wo,
                    product_code=product_codes[i],
                    product_name=product_names[i],
                    material=materials[i],
                    quantity=int(quantities[i] or 0),
                    unit=units[i]
                )

                dates = request.POST.getlist(f"delivery_date_{i}[]")
                qtys = request.POST.getlist(f"delivery_qty_{i}[]")

                for d, q in zip(dates, qtys):
                    if d:
                        WorkOrderDelivery.objects.create(
                            item=item,
                            delivery_date=d,
                            quantity=int(q or 0)
                        )

        return redirect("po_qu:workorder_detail", wo_id=wo.id)

    return render(request, "po_qu/workorder/edit_workorder.html", {
        "wo": wo,
        "edit_mode": True
    })


# ==========================================================
# 🔷 WORKORDER KANBAN
# ==========================================================

# ==========================================================
# 🔷 PDF
# ==========================================================
@login_required
def generate_workorder_pdf(request, wo_id):

    wo = get_object_or_404(WorkOrder, id=wo_id)

    template = get_template("po_qu/workorder/workorder_pdf.html")

    html = template.render({
        "wo": wo,
        "items": wo.items.all(),
        "logo_path": request.build_absolute_uri("/static/img/Brand_Logo_Square_copy.png"),
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=WO_{wo.id}.pdf'

    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)

    return response



# ===========================================================
# ========================= RFQ FORMATE =====================
# ===========================================================

@login_required
def create_rfq(request):

    if request.method == "POST":

        # =====================================================
        # WORKORDER ITEM ID
        # =====================================================

        item_id = request.POST.get("item_id")

        if not item_id:

            item_id = request.GET.get("item_id")

        # =====================================================
        # COMMERCIAL REQUIREMENTS
        # =====================================================

        commercial_requirements = ", ".join(

            request.POST.getlist(
                "commercial_requirements[]"
            )

        )

        # =====================================================
        # CERTIFICATION REQUIREMENTS
        # =====================================================

        certification_requirement = ", ".join(

            request.POST.getlist(
                "certification_requirement[]"
            )

        )

        # =====================================================
        # CREATE RFQ
        # =====================================================

        rfq = RFQ.objects.create(

            # =================================================
            # BASIC
            # =================================================

            rfq_date=request.POST.get(
                "rfq_date"
            ),

            required_delivery_date=request.POST.get(
                "required_delivery_date"
            ),

            company_name=request.POST.get(
                "company_name"
            ),

            contact_person=request.POST.get(
                "contact_person"
            ),

            email=request.POST.get(
                "email"
            ),

            phone=request.POST.get(
                "phone"
            ),

            # =================================================
            # DELIVERY
            # =================================================

            delivery_location=request.POST.get(
                "delivery_location"
            ),

            partial_delivery=request.POST.get(
                "partial_delivery"
            ) or "",

            # =================================================
            # TECHNICAL
            # =================================================

            material_grade=request.POST.get(
                "material_grade"
            ) or "",

            applicable_standard=request.POST.get(
                "applicable_standard"
            ) or "",

            heat_treatment=request.POST.get(
                "heat_treatment"
            ) or "",

            surface_condition=request.POST.get(
                "surface_condition"
            ) or "",

            packing_traceability=request.POST.get(
                "packing_traceability"
            ) or "",

            certification_requirement=
            certification_requirement,

            counterfeit_prevention=request.POST.get(
                "counterfeit_prevention"
            ) or "",

            # =================================================
            # COMMERCIAL
            # =================================================

            freight_terms=request.POST.get(
                "freight_terms"
            ) or "",

            payment_terms=request.POST.get(
                "payment_terms"
            ) or "",

            quotation_validity=request.POST.get(
                "quotation_validity"
            ) or "",

            commercial_requirements=
            commercial_requirements,

            # =================================================
            # TAX
            # =================================================

            discount_percentage=float(

                request.POST.get(
                    "discount"
                ) or 0

            ),

            cgst_percentage=float(

                request.POST.get(
                    "cgst"
                ) or 0

            ),

            sgst_percentage=float(

                request.POST.get(
                    "sgst"
                ) or 0

            ),

            igst_percentage=float(

                request.POST.get(
                    "igst"
                ) or 0

            ),

            # =================================================
            # NOTES
            # =================================================

            note=request.POST.get(
                "note"
            ) or "",

            compliance_statement=request.POST.get(
                "compliance_statement"
            ) or "",

            # =================================================
            # USER
            # =================================================

            created_by=request.user

        )

        # =====================================================
        # ITEMS
        # =====================================================

        material_names = request.POST.getlist(
            "material_name[]"
        )

        material_codes = request.POST.getlist(
            "material_code_grade[]"
        )

        dimensions = request.POST.getlist(
            "material_dimensions[]"
        )

        qtys = request.POST.getlist(
            "quantity[]"
        )

        weights = request.POST.getlist(
            "total_weight[]"
        )

        prices = request.POST.getlist(
            "price_per_kg[]"
        )

        uses = request.POST.getlist(
            "intended_use[]"
        )

        # =====================================================
        # CREATE ITEMS
        # =====================================================

        for (
            name,
            code,
            dimension,
            qty,
            weight,
            price,
            use
        ) in zip(

            material_names,

            material_codes,

            dimensions,

            qtys,

            weights,

            prices,

            uses

        ):

            # =================================================
            # SKIP EMPTY ROWS
            # =================================================

            if not name:

                continue

            # =================================================
            # CREATE ITEM
            # =================================================

            RFQItem.objects.create(

                rfq=rfq,

                material_name=name,

                material_code_grade=code,

                material_dimensions=dimension,

                quantity=float(
                    qty or 0
                ),

                total_weight=float(
                    weight or 0
                ),

                price_per_kg=float(
                    price or 0
                ),

                intended_use=use or ""

            )

        # =====================================================
        # LINK RFQ TO WORKORDER ITEM
        # =====================================================

        if item_id:

            try:

                item = WorkOrderItem.objects.get(
                    id=item_id
                )

                item.rfq_id = rfq.rfq_number

                item.save()

            except WorkOrderItem.DoesNotExist:

                pass

        # =====================================================
        # SUCCESS
        # =====================================================

        messages.success(

            request,

            "RFQ Created Successfully"

        )

        return redirect(

            "po_qu:rfq_detail",

            rfq_id=rfq.id

        )

    # =========================================================
    # PAGE
    # =========================================================

    return render(

        request,

        "po_qu/rfq/create_rfq.html"

    )




# ================================================================================
# ================================= RFQ LIST =====================================
# ================================================================================
@login_required
def rfq_list(request):

    rfqs = RFQ.objects.all().order_by(
        "-id"
    )

    return render(

        request,

        "po_qu/rfq/rfq_list.html",

        {

            "rfqs": rfqs

        }

    )


# ================================================================================
# ================================ RFQ DETAIL ====================================
# ================================================================================
@login_required
def rfq_detail(request, rfq_id):

    # =====================================================
    # GET RFQ
    # =====================================================

    rfq = get_object_or_404(

        RFQ.objects.prefetch_related(
            "items"
        ),

        id=rfq_id

    )

    # =====================================================
    # SUBTOTAL
    # =====================================================

    subtotal = Decimal("0.00")

    for item in rfq.items.all():

        subtotal += Decimal(
            item.total_price or 0
        )

    # =====================================================
    # DISCOUNT
    # =====================================================

    discount_amount = (

        subtotal *

        Decimal(
            rfq.discount_percentage or 0
        )

        / Decimal("100")

    )

    # =====================================================
    # TAXABLE
    # =====================================================

    taxable_amount = (
        subtotal - discount_amount
    )

    # =====================================================
    # CGST
    # =====================================================

    cgst_amount = (

        taxable_amount *

        Decimal(
            rfq.cgst_percentage or 0
        )

        / Decimal("100")

    )

    # =====================================================
    # SGST
    # =====================================================

    sgst_amount = (

        taxable_amount *

        Decimal(
            rfq.sgst_percentage or 0
        )

        / Decimal("100")

    )

    # =====================================================
    # IGST
    # =====================================================

    igst_amount = (

        taxable_amount *

        Decimal(
            rfq.igst_percentage or 0
        )

        / Decimal("100")

    )

    # =====================================================
    # GRAND TOTAL
    # =====================================================

    grand_total = (

        taxable_amount +

        cgst_amount +

        sgst_amount +

        igst_amount

    )

    # =====================================================
    # PAGE
    # =====================================================

    return render(

        request,

        "po_qu/rfq/rfq_detail.html",

        {

            "rfq": rfq,

            # =============================================
            # TOTALS
            # =============================================

            "subtotal": subtotal,

            "discount_amount": discount_amount,

            "taxable_amount": taxable_amount,

            "cgst_amount": cgst_amount,

            "sgst_amount": sgst_amount,

            "igst_amount": igst_amount,

            "grand_total": grand_total,

        }

    )

@login_required
def edit_rfq(request, rfq_id):

    # =====================================================
    # GET RFQ
    # =====================================================

    rfq = get_object_or_404(

        RFQ.objects.prefetch_related(
            "items"
        ),

        id=rfq_id

    )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        # =================================================
        # COMMERCIAL REQUIREMENTS
        # =================================================

        commercial_requirements = ", ".join(

            request.POST.getlist(
                "commercial_requirements[]"
            )

        )

        # =================================================
        # CERTIFICATION REQUIREMENTS
        # =================================================

        certification_requirement = ", ".join(

            request.POST.getlist(
                "certification_requirement[]"
            )

        )

        # =================================================
        # BASIC
        # =================================================

        rfq.rfq_date = request.POST.get(
            "rfq_date"
        )

        rfq.required_delivery_date = request.POST.get(
            "required_delivery_date"
        )

        rfq.company_name = request.POST.get(
            "company_name"
        )

        rfq.contact_person = request.POST.get(
            "contact_person"
        )

        rfq.email = request.POST.get(
            "email"
        )

        rfq.phone = request.POST.get(
            "phone"
        )

        # =================================================
        # DELIVERY
        # =================================================

        rfq.delivery_location = request.POST.get(
            "delivery_location"
        ) or ""

        rfq.partial_delivery = request.POST.get(
            "partial_delivery"
        ) or ""

        # =================================================
        # TECHNICAL
        # =================================================

        rfq.material_grade = request.POST.get(
            "material_grade"
        ) or ""

        rfq.applicable_standard = request.POST.get(
            "applicable_standard"
        ) or ""

        rfq.heat_treatment = request.POST.get(
            "heat_treatment"
        ) or ""

        rfq.surface_condition = request.POST.get(
            "surface_condition"
        ) or ""

        rfq.packing_traceability = request.POST.get(
            "packing_traceability"
        ) or ""

        rfq.certification_requirement = (
            certification_requirement
        )

        rfq.counterfeit_prevention = request.POST.get(
            "counterfeit_prevention"
        ) or ""

        # =================================================
        # TAX
        # =================================================

        rfq.discount_percentage = float(

            request.POST.get(
                "discount"
            ) or 0

        )

        rfq.cgst_percentage = float(

            request.POST.get(
                "cgst"
            ) or 0

        )

        rfq.sgst_percentage = float(

            request.POST.get(
                "sgst"
            ) or 0

        )

        rfq.igst_percentage = float(

            request.POST.get(
                "igst"
            ) or 0

        )

        # =================================================
        # COMMERCIAL
        # =================================================

        rfq.commercial_requirements = (
            commercial_requirements
        )

        rfq.freight_terms = request.POST.get(
            "freight_terms"
        ) or ""

        rfq.payment_terms = request.POST.get(
            "payment_terms"
        ) or ""

        rfq.quotation_validity = request.POST.get(
            "quotation_validity"
        ) or ""

        # =================================================
        # NOTES
        # =================================================

        rfq.compliance_statement = request.POST.get(
            "compliance_statement"
        ) or ""

        rfq.note = request.POST.get(
            "note"
        ) or ""

        # =================================================
        # SAVE RFQ
        # =================================================

        rfq.save()

        # =================================================
        # DELETE OLD ITEMS
        # =================================================

        rfq.items.all().delete()

        # =================================================
        # ITEMS
        # =================================================

        material_names = request.POST.getlist(
            "material_name[]"
        )

        material_codes = request.POST.getlist(
            "material_code_grade[]"
        )

        dimensions = request.POST.getlist(
            "material_dimensions[]"
        )

        qtys = request.POST.getlist(
            "quantity[]"
        )

        weights = request.POST.getlist(
            "total_weight[]"
        )

        prices = request.POST.getlist(
            "price_per_kg[]"
        )

        uses = request.POST.getlist(
            "intended_use[]"
        )

        # =================================================
        # CREATE ITEMS
        # =================================================

        for (
            name,
            code,
            dimension,
            qty,
            weight,
            price,
            use
        ) in zip(

            material_names,

            material_codes,

            dimensions,

            qtys,

            weights,

            prices,

            uses

        ):

            if not name:

                continue

            RFQItem.objects.create(

                rfq=rfq,

                material_name=name,

                material_code_grade=code,

                material_dimensions=dimension,

                quantity=float(
                    qty or 0
                ),

                total_weight=float(
                    weight or 0
                ),

                price_per_kg=float(
                    price or 0
                ),

                intended_use=use or ""

            )

        # =================================================
        # SUCCESS
        # =================================================

        messages.success(

            request,

            "RFQ Updated Successfully"

        )

        return redirect(

            "po_qu:rfq_detail",

            rfq_id=rfq.id

        )

    # =====================================================
    # PAGE
    # =====================================================

    return render(

        request,

        "po_qu/rfq/create_rfq.html",

        {

            "rfq": rfq,

            "edit_mode": True

        }

    )