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
# =========================================================
# SUPPLIER DETAIL PAGE
# =========================================================

@login_required
def supplier_detail(request, supplier_id):

    # =====================================
    # GET SUPPLIER
    # =====================================

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    # =====================================
    # RELATED DATA
    # =====================================

    stages = supplier.stages.all()

    documents = supplier.documents.all()

    audits = supplier.audit_requests.all().order_by(
        '-created_at'
    )

    activities = supplier.activities.all()

    evaluation = SupplierEvaluation.objects.filter(
        supplier=supplier
    ).first()

    # =====================================
    # APPROVAL HISTORY
    # =====================================

    approvals = SupplierAuditApprovalHistory.objects.filter(
        audit_request__supplier=supplier
    ).order_by(
        '-action_date'
    )

    # =====================================
    # APPROVED SUPPLIER LIST
    # =====================================

    asl = ApprovedSupplierList.objects.filter(
        supplier=supplier
    ).first()

    # =====================================
    # CONTEXT
    # =====================================

    total_audits = audits.count()

    open_audits = audits.exclude(
        status='closed'
    ).count()

    completed_audits = audits.filter(
        status='completed'
    ).count()

    context = {

        'supplier': supplier,

        'stages': stages,

        'documents': documents,

        'audits': audits,

        'approvals': approvals,

        'activities': activities,

        'evaluation': evaluation,

        'asl': asl,

        'total_audits': total_audits,

        'open_audits': open_audits,

        'completed_audits': completed_audits,

    }

    # =====================================
    # RENDER PAGE
    # =====================================

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
def upload_document(request, supplier_id):

    # =====================================
    # GET SUPPLIER
    # =====================================

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    # =====================================
    # UPLOAD DOCUMENT
    # =====================================

    if request.method == "POST":

        SupplierDocument.objects.create(

            supplier=supplier,

            document_name=request.POST.get(
                "document_name"
            ),

            document_file=request.FILES.get(
                "document_file"
            ),

            version=request.POST.get(
                "version"
            ),

            expiry_date=request.POST.get(
                "expiry_date"
            ),

            uploaded_by=request.user

        )

        # =====================================
        # ACTIVITY LOG
        # =====================================

        SupplierActivity.objects.create(

            supplier=supplier,

            activity="Document Uploaded",

            description=(
                f"Document "
                f"{request.POST.get('document_name')} "
                f"uploaded successfully"
            ),

            performed_by=request.user

        )

        messages.success(

            request,

            "Document uploaded successfully."

        )

        return redirect(

            "upload_document",

            supplier_id=supplier.id

        )

    # =====================================
    # DOCUMENT LIST
    # =====================================

    documents = SupplierDocument.objects.filter(

        supplier=supplier

    ).order_by(

        "-uploaded_at"

    )

    # =====================================
    # CONTEXT
    # =====================================

    context = {

        "supplier": supplier,

        "documents": documents,

    }

    return render(

        request,

        "sm/sm_upload_document.html",

        context

    )


# =========================================================
# SUPPLIER EVALUATION
# =========================================================
@login_required
def supplier_evaluation(request, supplier_id):

    # =====================================
    # GET SUPPLIER
    # =====================================

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    # =====================================
    # GET / CREATE EVALUATION
    # =====================================

    evaluation, created = SupplierEvaluation.objects.get_or_create(
        supplier=supplier
    )

    # =====================================
    # SAVE EVALUATION
    # =====================================

    if request.method == "POST":

        # ---------------------------------
        # EVALUATION SCORES
        # ---------------------------------

        evaluation.quality_score = int(
            request.POST.get(
                "quality_score",
                0
            )
        )

        evaluation.delivery_score = int(
            request.POST.get(
                "delivery_score",
                0
            )
        )

        evaluation.cost_score = int(
            request.POST.get(
                "cost_score",
                0
            )
        )

        evaluation.communication_score = int(
            request.POST.get(
                "communication_score",
                0
            )
        )

        evaluation.documentation_score = int(
            request.POST.get(
                "documentation_score",
                0
            )
        )

        evaluation.technical_score = int(
            request.POST.get(
                "technical_score",
                0
            )
        )

        evaluation.qms_score = int(
            request.POST.get(
                "qms_score",
                0
            )
        )

        # ---------------------------------
        # COMMENTS & RECOMMENDATIONS
        # ---------------------------------

        evaluation.strengths = request.POST.get(
            "strengths",
            ""
        )

        evaluation.weak_areas = request.POST.get(
            "weak_areas",
            ""
        )

        evaluation.corrective_actions = request.POST.get(
            "corrective_actions",
            ""
        )

        # ---------------------------------
        # NEXT EVALUATION DATE
        # ---------------------------------

        next_date = request.POST.get(
            "next_evaluation_date",
            ""
        ).strip()

        if next_date:

            evaluation.next_evaluation_date = next_date

        else:

            evaluation.next_evaluation_date = None

        evaluation.remarks = request.POST.get(
            "remarks",
            ""
        )

        # ---------------------------------
        # EVALUATION INFO
        # ---------------------------------

        evaluation.evaluated_by = request.user

        evaluation.evaluated_at = timezone.now()

        # ---------------------------------
        # SAVE EVALUATION
        # ---------------------------------

        evaluation.save()

        # =====================================
        # UPDATE SUPPLIER SCORE
        # =====================================

        supplier.evaluation_score = (
            evaluation.percentage
        )

        # =====================================
        # UPDATE SUPPLIER RISK LEVEL
        # =====================================

        if evaluation.percentage >= 90:

            supplier.risk_level = "low"

        elif evaluation.percentage >= 75:

            supplier.risk_level = "medium"

        elif evaluation.percentage >= 60:

            supplier.risk_level = "high"

        else:

            supplier.risk_level = "critical"

        supplier.save()

        # =====================================
        # ACTIVITY LOG
        # =====================================

        SupplierActivity.objects.create(

            supplier=supplier,

            activity="Supplier Evaluation Completed",

            description=(
                f"Evaluation Score : "
                f"{evaluation.percentage}% | "
                f"Rating : "
                f"{evaluation.rating}"
            ),

            performed_by=request.user

        )

        # =====================================
        # SUCCESS MESSAGE
        # =====================================

        messages.success(

            request,

            "Supplier Evaluation Submitted Successfully"

        )

        return redirect(

            "supplier_detail",

            supplier_id=supplier.id

        )

    # =====================================
    # CONTEXT
    # =====================================

    context = {

        "supplier": supplier,

        "evaluation": evaluation,

    }

    # =====================================
    # RENDER PAGE
    # =====================================

    return render(

        request,

        "sm/supplier_evaluation.html",

        context

    )



@login_required
def risk_classification(request, supplier_id):

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    if request.method == "POST":

        # =====================================
        # RISK FACTORS
        # =====================================

        supplier.business_impact = request.POST.get(
            'business_impact',
            'Medium'
        )

        supplier.criticality = request.POST.get(
            'criticality',
            'Medium'
        )

        supplier.supply_risk = request.POST.get(
            'supply_risk',
            'Medium'
        )

        supplier.quality_risk = request.POST.get(
            'quality_risk',
            'Medium'
        )

        supplier.compliance_risk = request.POST.get(
            'compliance_risk',
            'Medium'
        )

        supplier.financial_risk = request.POST.get(
            'financial_risk',
            'Medium'
        )

        supplier.geographical_risk = request.POST.get(
            'geographical_risk',
            'Medium'
        )

        # =====================================
        # COMMENTS
        # =====================================

        supplier.risk_comments = request.POST.get(
            'comments',
            ''
        )

        supplier.mitigation_plan = request.POST.get(
            'mitigation_plan',
            ''
        )

        # =====================================
        # SCORE CALCULATION
        # =====================================

        score_map = {

            'Low': 1,

            'Medium': 2,

            'High': 4

        }

        supplier.risk_score = (

            score_map.get(
                supplier.business_impact,
                0
            )

            +

            score_map.get(
                supplier.criticality,
                0
            )

            +

            score_map.get(
                supplier.supply_risk,
                0
            )

            +

            score_map.get(
                supplier.quality_risk,
                0
            )

            +

            score_map.get(
                supplier.compliance_risk,
                0
            )

            +

            score_map.get(
                supplier.financial_risk,
                0
            )

            +

            score_map.get(
                supplier.geographical_risk,
                0
            )

        )

        # =====================================
        # RISK LEVEL
        # =====================================

        if supplier.risk_score <= 7:

            supplier.risk_level = 'low'
            supplier.risk_category = 'Approved Supplier'
            supplier.review_frequency = '12 Months'

        elif supplier.risk_score <= 12:

            supplier.risk_level = 'medium'
            supplier.risk_category = 'Controlled Supplier'
            supplier.review_frequency = '6 Months'

        elif supplier.risk_score <= 18:

            supplier.risk_level = 'high'
            supplier.risk_category = 'High Risk Supplier'
            supplier.review_frequency = '3 Months'

        else:

            supplier.risk_level = 'critical'
            supplier.risk_category = 'Critical Supplier'
            supplier.review_frequency = '1 Month'

        # =====================================
        # NEXT REVIEW DATE
        # =====================================

        from datetime import timedelta
        from django.utils import timezone

        if supplier.review_frequency == '12 Months':

            supplier.next_review_date = (
                timezone.now().date() +
                timedelta(days=365)
            )

        elif supplier.review_frequency == '6 Months':

            supplier.next_review_date = (
                timezone.now().date() +
                timedelta(days=180)
            )

        elif supplier.review_frequency == '3 Months':

            supplier.next_review_date = (
                timezone.now().date() +
                timedelta(days=90)
            )

        else:

            supplier.next_review_date = (
                timezone.now().date() +
                timedelta(days=30)
            )

        supplier.save()

        # =====================================
        # ACTIVITY LOG
        # =====================================

        SupplierActivity.objects.create(

            supplier=supplier,

            activity="Risk Assessment Completed",

            description=(
                f"Risk Score: {supplier.risk_score} | "
                f"Risk Level: {supplier.risk_level.upper()}"
            ),

            performed_by=request.user

        )

        messages.success(
            request,
            "Risk Classification Saved Successfully"
        )

        return redirect(
            'supplier_detail',
            supplier_id=supplier.id
        )

    # =====================================
    # RISK MATRIX VALUES
    # =====================================

    matrix_score_map = {

        'Low': 1,

        'Medium': 2,

        'High': 3,

    }

    impact_value = matrix_score_map.get(

        supplier.business_impact,

        1

    )

    likelihood_value = matrix_score_map.get(

        supplier.supply_risk,

        1

    )

    # =====================================
    # CONTEXT
    # =====================================

    context = {

        'supplier': supplier,

        'impact_value': impact_value,

        'likelihood_value': likelihood_value,

    }

    return render(

        request,

        'sm/risk_classification.html',

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



# =========================================================
# SUPPLIER AUDIT LIST
# =========================================================

@login_required
def supplier_audit_list(request):

    audits = SupplierAuditRequest.objects.select_related(
        'supplier'
    ).order_by(
        '-created_at'
    )

    context = {

        'audits': audits

    }

    return render(

        request,

        'sm/supplier_audit_list.html',

        context

    )


# =========================================================
# SUPPLIER AUDIT DASHBOARD
# =========================================================

@login_required
def supplier_audit_dashboard(
    request,
    supplier_id
):

    supplier = get_object_or_404(

        Supplier,

        id=supplier_id

    )

    audits = SupplierAuditRequest.objects.filter(

        supplier=supplier

    ).order_by(

        '-created_at'

    )

    total_audits = audits.count()

    open_audits = audits.exclude(

        status='closed'

    ).count()

    completed_audits = audits.filter(

        status='completed'

    ).count()

    context = {

        'supplier': supplier,

        'audits': audits,

        'total_audits': total_audits,

        'open_audits': open_audits,

        'completed_audits': completed_audits,

    }

    return render(

        request,

        'sm/supplier_audit_dashboard.html',

        context

    )


# =========================================================
# CREATE AUDIT REQUEST
# =========================================================


@login_required
def create_audit_request(
    request,
    supplier_id
):

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    if request.method == "POST":

        # =====================================
        # CREATE AUDIT REQUEST
        # =====================================

        audit_request = SupplierAuditRequest.objects.create(

            supplier=supplier,

            audit_type=request.POST.get(
                "audit_type"
            ),

            audit_category=request.POST.get(
                "audit_category"
            ),

            audit_criteria=request.POST.get(
                "audit_criteria"
            ),

            audit_trigger=request.POST.get(
                "audit_trigger"
            ),

            priority=request.POST.get(
                "priority"
            ),

            preferred_audit_date=request.POST.get(
                "preferred_audit_date"
            ),

            reason=request.POST.get(
                "reason"
            ),

            objectives=request.POST.get(
                "objectives"
            ),

            additional_notes=request.POST.get(
                "additional_notes"
            ),

            requested_by=request.user,

            status="draft"

        )

        # =====================================
        # SAVE AUDIT SCOPE
        # =====================================

        selected_scopes = request.POST.getlist(
            "audit_scope"
        )

        for scope_name in selected_scopes:

            scope_obj, created = (
                AuditScopeMaster.objects.get_or_create(
                    name=scope_name
                )
            )

            SupplierAuditScope.objects.create(

                audit_request=audit_request,

                scope=scope_obj

            )

        # =====================================
        # SAVE DEPARTMENTS
        # =====================================

        selected_departments = request.POST.getlist(
            "departments"
        )

        for department_name in selected_departments:

            department_obj, created = (
                DepartmentMaster.objects.get_or_create(
                    name=department_name
                )
            )

            SupplierAuditDepartment.objects.create(

                audit_request=audit_request,

                department=department_obj

            )

        # =====================================
        # SAVE ATTACHMENTS
        # =====================================

        attachments = request.FILES.getlist(
            "attachments"
        )

        for file in attachments:

            SupplierAuditAttachment.objects.create(

                audit_request=audit_request,

                file=file,

                uploaded_by=request.user

            )

        # =====================================
        # APPROVAL HISTORY
        # =====================================

        SupplierAuditApprovalHistory.objects.create(

            audit_request=audit_request,

            action="submitted",

            comments="Audit Request Created",

            action_by=request.user

        )

        # =====================================
        # UPDATE SUPPLIER STATUS
        # =====================================

        supplier.audit_status = (
            "Audit Requested"
        )

        supplier.save()

        # =====================================
        # ACTIVITY LOG
        # =====================================

        SupplierActivity.objects.create(

            supplier=supplier,

            activity="Audit Request Created",

            description=(
                f"Audit Request "
                f"{audit_request.request_no}"
            ),

            performed_by=request.user

        )

        messages.success(

            request,

            (
                f"Audit Request "
                f"{audit_request.request_no} "
                f"created successfully."
            )

        )

        return redirect(

            "supplier_detail",

            supplier_id=supplier.id

        )

    context = {

        "supplier": supplier,

        "audit_types":
        SupplierAuditRequest.AUDIT_TYPE_CHOICES,

        "audit_categories":
        SupplierAuditRequest.AUDIT_CATEGORY_CHOICES,

        "audit_criteria":
        SupplierAuditRequest.AUDIT_CRITERIA_CHOICES,

        "audit_triggers":
        SupplierAuditRequest.TRIGGER_CHOICES,

        "priorities":
        SupplierAuditRequest.PRIORITY_CHOICES,

        "scope_master":
        AuditScopeMaster.objects.filter(
            active=True
        ),

        "department_master":
        DepartmentMaster.objects.filter(
            active=True
        ),

        "deliverable_master":
        DeliverableMaster.objects.filter(
            active=True
        ),

    }

    return render(

        request,

        "sm/create_audit_request.html",

        context

    )

