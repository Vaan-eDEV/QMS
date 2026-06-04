from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import (
    login_required
)

from django.contrib import messages

from django.utils import timezone

from .models import (
    Visitor,
    VisitorBelonging
)


# =========================================================
# VISITOR DASHBOARD
# =========================================================

@login_required
def visitor_dashboard(request):

    visitors = (
        Visitor.objects
        .all()
        .order_by("-created_at")
    )

    inside_visitors = visitors.filter(
        status="CHECKED_IN"
    ).count()

    checked_out = visitors.filter(
        status="CHECKED_OUT"
    ).count()

    pending_visitors = visitors.filter(
        status="PENDING"
    ).count()

    return render(

        request,

        "visitors/visitors_dashboard.html",

        {

            "visitors": visitors,

            "inside_visitors": inside_visitors,

            "checked_out": checked_out,

            "pending_visitors": pending_visitors,

        }

    )


# =========================================================
# CREATE VISITOR
# =========================================================
@login_required
def create_visitor(request):

    import base64

    from django.core.files.base import (
        ContentFile
    )

    from django.contrib.auth import (
        get_user_model
    )

    User = get_user_model()

    # =====================================================
    # SAVE VISITOR
    # =====================================================

    if request.method == "POST":

        visitor = Visitor.objects.create(

            name=request.POST.get("name"),

            company=request.POST.get("company"),

            phone=request.POST.get("phone"),

            email=request.POST.get("email"),

            purpose=request.POST.get("purpose"),

            department=request.POST.get(
                "department"
            ),

            vehicle_number=request.POST.get(
                "vehicle_number"
            ),

            host_employee_id=request.POST.get(
                "host_employee"
            ),

            created_by=request.user,

            status="CHECKED_IN",

            check_in_time=timezone.now()

        )

        # =================================================
        # WEBCAM PHOTO SAVE
        # =================================================

        captured_photo = request.POST.get(
            "captured_photo"
        )

        if captured_photo:

            try:

                format, imgstr = (
                    captured_photo.split(
                        ";base64,"
                    )
                )

                ext = format.split("/")[-1]

                visitor.visitor_photo.save(

                    f"{visitor.visitor_id}.{ext}",

                    ContentFile(
                        base64.b64decode(imgstr)
                    ),

                    save=True

                )

            except Exception as e:

                print("PHOTO ERROR:", e)

        # =================================================
        # ID PROOF
        # =================================================

        if request.FILES.get("id_proof"):

            visitor.id_proof = request.FILES.get(
                "id_proof"
            )

            visitor.save()

        # =================================================
        # BELONGINGS
        # =================================================

        item_names = request.POST.getlist(
            "item_name[]"
        )

        quantities = request.POST.getlist(
            "quantity[]"
        )

        serials = request.POST.getlist(
            "serial_number[]"
        )

        remarks = request.POST.getlist(
            "remarks[]"
        )

        for i in range(len(item_names)):

            if item_names[i]:

                VisitorBelonging.objects.create(

                    visitor=visitor,

                    item_name=item_names[i],

                    quantity=quantities[i] or 1,

                    serial_number=serials[i],

                    remarks=remarks[i]

                )

        # =================================================
        # SUCCESS
        # =================================================

        messages.success(

            request,

            "Visitor created successfully"

        )

        return redirect(
            "visitors:visitor_dashboard"
        )

    # =====================================================
    # PAGE
    # =====================================================

    return render(

        request,

        "visitors/create_visitor.html",

        {

            "users": User.objects.all()

        }

    )

# =========================================================
# VISITOR DETAIL
# =========================================================

@login_required
def visitor_detail(request, visitor_id):

    visitor = get_object_or_404(

        Visitor,

        id=visitor_id

    )

    belongings = visitor.belongings.all()

    return render(

        request,

        "visitors/visitor_detail.html",

        {

            "visitor": visitor,

            "belongings": belongings,

        }

    )


# =========================================================
# CHECKOUT VISITOR
# =========================================================

@login_required
def checkout_visitor(request, visitor_id):

    visitor = get_object_or_404(

        Visitor,

        id=visitor_id

    )

    # ==============================================
    # RETURN BELONGINGS
    # ==============================================

    for item in visitor.belongings.all():

        returned = request.POST.get(

            f"returned_{item.id}"

        )

        if returned == "on":

            item.returned = True

            item.returned_at = timezone.now()

            item.save()

    # ==============================================
    # CHECK ALL RETURNED
    # ==============================================

    pending = visitor.belongings.filter(
        returned=False
    ).exists()

    if pending:

        messages.error(

            request,

            "All belongings must be returned"

        )

        return redirect(

            "visitors:visitor_detail",

            visitor.id

        )

    # ==============================================
    # CHECKOUT
    # ==============================================

    visitor.status = "CHECKED_OUT"

    visitor.check_out_time = timezone.now()

    visitor.save()

    messages.success(

        request,

        "Visitor checked out"

    )

    return redirect(
        "visitors:visitor_dashboard"
    )


@login_required
def visitor_pass(request, visitor_id):

    visitor = get_object_or_404(

        Visitor,

        id=visitor_id

    )

    return render(

        request,

        "visitors/visitor_pass.html",

        {

            "visitor": visitor

        }

    )