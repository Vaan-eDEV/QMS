from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.utils import timezone

from .models import *

# =========================================================
# SUPPLIER DASHBOARD
# =========================================================

@login_required
def supplier_dashboard(request):

    suppliers = Supplier.objects.all().order_by('-created_at')

    total_suppliers = suppliers.count()

    approved_suppliers = suppliers.filter(
        status='approved'
    ).count()

    pending_suppliers = suppliers.filter(
        status='in_progress'
    ).count()

    high_risk_suppliers = suppliers.filter(
        risk_level='high'
    ).count()

    context = {

        'suppliers': suppliers,

        'total_suppliers': total_suppliers,

        'approved_suppliers': approved_suppliers,

        'pending_suppliers': pending_suppliers,

        'high_risk_suppliers': high_risk_suppliers,

    }

    return render(
        request,
        'sm/sm_dashboard.html',
        context
    )


# =========================================================
# SUPPLIER LIST
# =========================================================

@login_required
def supplier_list(request):

    suppliers = Supplier.objects.all().order_by(
        '-created_at'
    )

    context = {

        'suppliers': suppliers

    }

    return render(
        request,
        'sm/supplier_list.html',
        context
    )


# =========================================================
# SUPPLIER DETAIL PAGE
# =========================================================

@login_required
def supplier_detail(request, supplier_id):

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    stages = supplier.stages.all()

    documents = supplier.documents.all()

    audits = supplier.audits.all()

    approvals = supplier.approvals.all()

    activities = supplier.activities.all()

    evaluation = SupplierEvaluation.objects.filter(
        supplier=supplier
    ).first()

    context = {

        'supplier': supplier,

        'stages': stages,

        'documents': documents,

        'audits': audits,

        'approvals': approvals,

        'activities': activities,

        'evaluation': evaluation,

    }

    return render(
        request,
        'sm/supplier_detail.html',
        context
    )


# =========================================================
# CREATE SUPPLIER
# =========================================================
@login_required
def create_supplier(request):

    if request.method == "POST":

        # =====================================
        # GET FORM DATA
        # =====================================

        supplier_code = request.POST.get(
            'supplier_code'
        )

        supplier_name = request.POST.get(
            'supplier_name'
        )

        # =====================================
        # VALIDATION
        # =====================================

        if not supplier_code:

            messages.error(
                request,
                "Supplier code is required"
            )

            return redirect(
                'create_supplier'
            )

        if not supplier_name:

            messages.error(
                request,
                "Supplier name is required"
            )

            return redirect(
                'create_supplier'
            )

        # =====================================
        # DUPLICATE CHECK
        # =====================================

        existing_supplier = Supplier.objects.filter(
            supplier_code=supplier_code
        ).exists()

        if existing_supplier:

            messages.error(
                request,
                "Supplier code already exists"
            )

            return redirect(
                'create_supplier'
            )

        try:

            # =====================================
            # CREATE SUPPLIER
            # =====================================

            supplier = Supplier.objects.create(

                supplier_code=supplier_code,

                supplier_name=supplier_name,

                supplier_type=request.POST.get(
                    'supplier_type'
                ),

                category=request.POST.get(
                    'category'
                ),

                contact_person=request.POST.get(
                    'contact_person'
                ),

                email=request.POST.get(
                    'email'
                ),

                phone=request.POST.get(
                    'phone'
                ),

                website=request.POST.get(
                    'website'
                ),

                address=request.POST.get(
                    'address'
                ),

                city=request.POST.get(
                    'city'
                ),

                state=request.POST.get(
                    'state'
                ),

                country=request.POST.get(
                    'country'
                ),

                postal_code=request.POST.get(
                    'postal_code'
                ),

                gst_number=request.POST.get(
                    'gst_number'
                ),

                pan_number=request.POST.get(
                    'pan_number'
                ),

                registration_number=request.POST.get(
                    'registration_number'
                ),

                created_by=request.user,

                status='in_progress'

            )

            # =====================================
            # DEFAULT WORKFLOW STAGES
            # =====================================

            stages = [

                "Registration",

                "Initial Screening",

                "Document Verification",

                "Evaluation & Scorecard",

                "Risk Classification",

                "Supplier Audit",

                "Final Approval",

                "ASL Entry",

            ]

            # =====================================
            # CREATE STAGES
            # =====================================

            for index, stage in enumerate(stages):

                SupplierStage.objects.create(

                    supplier=supplier,

                    stage_no=index + 1,

                    stage_name=stage,

                    status='pending'

                )

            # =====================================
            # COMPLETE FIRST STAGE
            # =====================================

            first_stage = supplier.stages.first()

            if first_stage:

                first_stage.status = 'completed'

                first_stage.completed_date = timezone.now()

                first_stage.save()

            # =====================================
            # ACTIVITY LOG
            # =====================================

            SupplierActivity.objects.create(

                supplier=supplier,

                activity="Supplier Created",

                description="New supplier registration created",

                performed_by=request.user

            )

            # =====================================
            # SUCCESS MESSAGE
            # =====================================

            messages.success(
                request,
                "Supplier created successfully"
            )

            # =====================================
            # REDIRECT
            # =====================================

            return redirect(

                'supplier_detail',

                supplier_id=supplier.id

            )

        except Exception as e:

            messages.error(

                request,

                f"Error creating supplier: {str(e)}"

            )

            return redirect(
                'create_supplier'
            )

    # =====================================
    # GET REQUEST
    # =====================================

    return render(

        request,

        'sm/create_supplier.html'

    )


# =========================================================
# UPDATE STAGE STATUS
# =========================================================

@login_required
def update_stage_status(

    request,

    stage_id

):

    stage = get_object_or_404(

        SupplierStage,

        id=stage_id

    )

    if request.method == "POST":

        status = request.POST.get(
            'status'
        )

        remarks = request.POST.get(
            'remarks'
        )

        stage.status = status

        stage.remarks = remarks

        if status == 'completed':

            stage.completed_date = timezone.now()

        stage.save()

        # =====================================
        # UPDATE CURRENT STAGE
        # =====================================

        supplier = stage.supplier

        next_stage = supplier.stages.filter(
            status='pending'
        ).first()

        if next_stage:

            supplier.current_stage = next_stage.stage_no

        else:

            supplier.current_stage = 8

            supplier.status = 'approved'

        supplier.save()

        # =====================================
        # ACTIVITY LOG
        # =====================================

        SupplierActivity.objects.create(

            supplier=supplier,

            activity=f"{stage.stage_name} Updated",

            description=f"Stage updated to {status}",

            performed_by=request.user

        )

        messages.success(
            request,
            "Stage updated successfully"
        )

        return redirect(
            'supplier_detail',
            supplier_id=supplier.id
        )

    context = {

        'stage': stage

    }

    return render(
        request,
        'sm/update_stage.html',
        context
    )


# =========================================================
# DOCUMENT UPLOAD
# =========================================================

@login_required
def upload_document(

    request,

    supplier_id

):

    supplier = get_object_or_404(

        Supplier,

        id=supplier_id

    )

    if request.method == "POST":

        SupplierDocument.objects.create(

            supplier=supplier,

            document_name=request.POST.get(
                'document_name'
            ),

            document_file=request.FILES.get(
                'document_file'
            ),

            version=request.POST.get(
                'version'
            ),

            expiry_date=request.POST.get(
                'expiry_date'
            ),

            uploaded_by=request.user

        )

        SupplierActivity.objects.create(

            supplier=supplier,

            activity="Document Uploaded",

            description="Supplier document uploaded",

            performed_by=request.user

        )

        messages.success(
            request,
            "Document uploaded successfully"
        )

        return redirect(
            'supplier_detail',
            supplier_id=supplier.id
        )

    context = {

        'supplier': supplier

    }

    return render(
        request,
        'sm/upload_document.html',
        context
    )


# =========================================================
# SUPPLIER EVALUATION
# =========================================================
@login_required
def supplier_evaluation(request, supplier_id):

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    evaluation, created = SupplierEvaluation.objects.get_or_create(

        supplier=supplier

    )

    if request.method == "POST":

        evaluation.quality_score = int(
            request.POST.get('quality_score', 0)
        )

        evaluation.delivery_score = int(
            request.POST.get('delivery_score', 0)
        )

        evaluation.technical_score = int(
            request.POST.get('technical_score', 0)
        )

        evaluation.documentation_score = int(
            request.POST.get('documentation_score', 0)
        )

        evaluation.compliance_score = int(
            request.POST.get('compliance_score', 0)
        )

        evaluation.commercial_score = int(
            request.POST.get('commercial_score', 0)
        )

        evaluation.remarks = request.POST.get(
            'remarks'
        )

        evaluation.evaluated_by = request.user

        evaluation.evaluated_at = timezone.now()

        evaluation.save()

        # =====================================
        # UPDATE SUPPLIER SCORE
        # =====================================

        supplier.evaluation_score = evaluation.total_score

        # =====================================
        # RISK LEVEL
        # =====================================

        if evaluation.total_score >= 75:

            supplier.risk_level = 'low'

        elif evaluation.total_score >= 60:

            supplier.risk_level = 'medium'

        else:

            supplier.risk_level = 'high'

        supplier.save()

        # =====================================
        # ACTIVITY LOG
        # =====================================

        SupplierActivity.objects.create(

            supplier=supplier,

            activity="Supplier Evaluation Completed",

            description=f"Supplier evaluated with total score {evaluation.total_score}",

            performed_by=request.user

        )

        messages.success(

            request,

            "Supplier evaluation submitted successfully"

        )

        return redirect(

            'supplier_detail',

            supplier_id=supplier.id

        )

    context = {

        'supplier': supplier,

        'evaluation': evaluation

    }

    return render(

        request,

        'sm/supplier_evaluation.html',

        context

    )

# =========================================================
# DELETE SUPPLIER
# =========================================================

@login_required
def delete_supplier(

    request,

    supplier_id

):

    supplier = get_object_or_404(

        Supplier,

        id=supplier_id

    )

    if request.method == "POST":

        supplier.delete()

        messages.success(
            request,
            "Supplier deleted successfully"
        )

        return redirect(
            'supplier_list'
        )

    context = {

        'supplier': supplier

    }

    return render(
        request,
        'sm/delete_supplier.html',
        context
    )