
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from .models import Feedback

import random

from datetime import datetime, timedelta


# ==========================================
# FEEDBACK LIST PAGE
# ==========================================

def feedback_list(request):

    feedbacks = Feedback.objects.all().order_by('-id')


    # SEARCH FILTERS

    feedback_no = request.GET.get('feedback_no')

    customer = request.GET.get('customer')

    feedback_type = request.GET.get('feedback_type')

    status = request.GET.get('status')

    severity = request.GET.get('severity')

    category = request.GET.get('category')

    date_from = request.GET.get('date_from')

    date_to = request.GET.get('date_to')


    if feedback_no:

        feedbacks = feedbacks.filter(

            feedback_no__icontains=feedback_no

        )


    if customer:

        feedbacks = feedbacks.filter(

            customer_name__icontains=customer

        )


    if feedback_type:

        feedbacks = feedbacks.filter(

            feedback_type=feedback_type

        )


    if status:

        feedbacks = feedbacks.filter(

            status=status

        )


    if severity:

        feedbacks = feedbacks.filter(

            severity=severity

        )


    if category:

        feedbacks = feedbacks.filter(

            category__icontains=category

        )


    if date_from:

        feedbacks = feedbacks.filter(

            date_received__gte=date_from

        )


    if date_to:

        feedbacks = feedbacks.filter(

            date_received__lte=date_to

        )


    # PAGINATION

    paginator = Paginator(feedbacks, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)


    context = {

        'page_obj': page_obj,

        'total_feedbacks': feedbacks.count(),

    }


    return render(

        request,

        'feedback/feedback_list.html',

        context

    )


# ==========================================
# CREATE FEEDBACK
# ==========================================

def feedback_form(request):
    
  

    if request.method == 'POST':

        try:

            # AUTO FEEDBACK NUMBER

            random_number = random.randint(1000, 9999)

            feedback_number = f"CF-2026-{random_number}"


            # DUE DATE AUTO

            due_date = None

            target_date = request.POST.get(
                'target_investigation_date'
            )

            if target_date:

                due_date = target_date


            # CREATE RECORD

            feedback = Feedback.objects.create(

                # MAIN DETAILS

                feedback_no=feedback_number,

                date_received=request.POST.get(
                    'date_received'
                ),

                received_by=request.POST.get(
                    'received_by'
                ),

                customer_name=request.POST.get(
                    'customer_name'
                ),

                customer_contact=request.POST.get(
                    'customer_contact'
                ),

                customer_email=request.POST.get(
                    'customer_email'
                ),

                product_name=request.POST.get(
                    'product_name'
                ),

                part_number=request.POST.get(
                    'part_number'
                ),

                lot_batch_number=request.POST.get(
                    'lot_batch_number'
                ),

                sales_order_no=request.POST.get(
                    'sales_order_no'
                ),

                # FEEDBACK DETAILS

                feedback_type=request.POST.get(
                    'feedback_type'
                ),

                category=request.POST.get(
                    'category'
                ),

                severity=request.POST.get(
                    'severity'
                ),

                source_of_feedback=request.POST.get(
                    'source_of_feedback'
                ),

                reference_document=request.POST.get(
                    'reference_document'
                ),

                description=request.POST.get(
                    'description'
                ),

                attachment=request.FILES.get(
                    'attachment'
                ),

                # ADDITIONAL INFO

                date_of_occurrence=request.POST.get(
                    'date_of_occurrence'
                ),

                location_site=request.POST.get(
                    'location_site'
                ),

                department=request.POST.get(
                    'department'
                ),

                impact_on_customer=request.POST.get(
                    'impact_on_customer'
                ),

                immediate_action_taken=request.POST.get(
                    'immediate_action_taken'
                ),

                # INTERNAL USE

                priority=request.POST.get(
                    'priority'
                ),

                assigned_to=request.POST.get(
                    'assigned_to'
                ),

                target_investigation_date=request.POST.get(
                    'target_investigation_date'
                ),

                remarks=request.POST.get(
                    'remarks'
                ),

                # STATUS

                status='Open',

                due_date=due_date,

                # NOTIFICATION

                notify_users=True if request.POST.get(
                    'notify_users'
                ) else False

            )


            return redirect('feedback_list')


        except Exception as e:

            return render(

                request,

                'feedback/feedback_form.html',

                {
                   
                    'error': str(e)
                }

            )


    return render(

        request,

        'feedback/feedback_form.html',
       

    )


# ==========================================
# VIEW SINGLE FEEDBACK
# ==========================================

def feedback_detail(request, id):

    feedback = get_object_or_404(

        Feedback,

        id=id

    )

    return render(

        request,

        'feedback/feedback_detail.html',

        {
            'feedback': feedback
        }

    )


# ==========================================
# DELETE FEEDBACK
# ==========================================

def delete_feedback(request, id):

    feedback = get_object_or_404(

        Feedback,

        id=id

    )

    feedback.delete()

    return redirect('feedback_list')


# ==========================================
# UPDATE STATUS
# ==========================================

def update_feedback_status(request, id):

    feedback = get_object_or_404(

        Feedback,

        id=id

    )

    if request.method == 'POST':

        feedback.status = request.POST.get(
            'status'
        )

        feedback.save()

    return redirect('feedback_list')


# ==========================================
# EDIT FEEDBACK
# ==========================================



def edit_feedback(request, id):

    feedback = get_object_or_404(

        Feedback,

        id=id

    )



    if request.method == 'POST':

        try:

            # ==========================================
            # GENERAL INFORMATION
            # ==========================================

            feedback.date_received = request.POST.get(
                'date_received'
            )

            feedback.received_by = request.POST.get(
                'received_by'
            )

            feedback.customer_name = request.POST.get(
                'customer_name'
            )

            feedback.customer_contact = request.POST.get(
                'customer_contact'
            )

            feedback.customer_email = request.POST.get(
                'customer_email'
            )

            feedback.product_name = request.POST.get(
                'product_name'
            )

            feedback.part_number = request.POST.get(
                'part_number'
            )

            feedback.lot_batch_number = request.POST.get(
                'lot_batch_number'
            )

            feedback.sales_order_no = request.POST.get(
                'sales_order_no'
            )

            feedback.feedback_type = request.POST.get(
                'feedback_type'
            )

            feedback.category = request.POST.get(
                'category'
            )

            feedback.severity = request.POST.get(
                'severity'
            )

            feedback.source_of_feedback = request.POST.get(
                'source_of_feedback'
            )

            feedback.reference_document = request.POST.get(
                'reference_document'
            )

            feedback.description = request.POST.get(
                'description'
            )

            # ==========================================
            # ATTACHMENT
            # ==========================================

            if request.FILES.get('attachment'):

                feedback.attachment = request.FILES.get(
                    'attachment'
                )

            # ==========================================
            # ADDITIONAL INFORMATION
            # ==========================================

            feedback.date_of_occurrence = request.POST.get(
                'date_of_occurrence'
            )

            feedback.location_site = request.POST.get(
                'location_site'
            )

            feedback.department = request.POST.get(
                'department'
            )

            feedback.impact_on_customer = request.POST.get(
                'impact_on_customer'
            )

            feedback.immediate_action_taken = request.POST.get(
                'immediate_action_taken'
            )

            # ==========================================
            # INTERNAL USE
            # ==========================================

            feedback.priority = request.POST.get(
                'priority'
            )

            feedback.assigned_to = request.POST.get(
                'assigned_to'
            )

            feedback.target_investigation_date = request.POST.get(
                'target_investigation_date'
            )

            feedback.status = request.POST.get(
                'status'
            )

            feedback.remarks = request.POST.get(
                'remarks'
            )

            feedback.notify_users = True if request.POST.get(
                'notify_users'
            ) else False

            # ==========================================
            # SAVE
            # ==========================================

            feedback.save()

            return redirect(

                'feedback_detail',

                id=feedback.id

            )

        except Exception as e:

            return render(

                request,

                'feedback/edit_feedback.html',

                {
                    'feedback': feedback,
                   
                    'error': str(e)
                }

            )

    return render(

        request,

        'feedback/edit_feedback.html',

        {
            'feedback': feedback,
            
        }

    )



from django.shortcuts import render
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.utils.timezone import now
from datetime import timedelta

from .models import Feedback


# ==========================================================
# FEEDBACK DASHBOARD
# ==========================================================

def feedback_dashboard(request):

    current_year = now().year

    feedbacks = Feedback.objects.all()

    # ==========================================================
    # KPI COUNTS
    # ==========================================================

    total_feedback = feedbacks.count()

    open_feedback = feedbacks.filter(
        status="Open"
    ).count()

    overdue_feedback = feedbacks.filter(
        status="Open",
        due_date__lt=now().date()
    ).count()

    critical_feedback = feedbacks.filter(
        severity="Critical"
    ).count()

    closed_feedback = feedbacks.filter(
        status="Closed"
    )

    # ==========================================================
    # AVG CLOSURE TIME
    # ==========================================================

    avg_closure = closed_feedback.annotate(

        closure_time=ExpressionWrapper(

            F("updated_at") - F("date_received"),

            output_field=DurationField()

        )

    ).aggregate(

        avg_time=Avg("closure_time")

    )

    avg_closure_days = 0

    if avg_closure["avg_time"]:

        avg_closure_days = round(

            avg_closure["avg_time"].days +

            (

                avg_closure["avg_time"].seconds / 86400

            ),

            1

        )

    # ==========================================================
    # MONTHLY TREND DATA
    # ==========================================================

    monthly_total = []
    monthly_complaints = []
    monthly_suggestions = []
    monthly_appreciations = []

    for month in range(1, 13):

        month_feedbacks = feedbacks.filter(

            date_received__year=current_year,

            date_received__month=month

        )

        monthly_total.append(

            month_feedbacks.count()

        )

        monthly_complaints.append(

            month_feedbacks.filter(
                feedback_type="Complaint"
            ).count()

        )

        monthly_suggestions.append(

            month_feedbacks.filter(
                feedback_type="Suggestion"
            ).count()

        )

        monthly_appreciations.append(

            month_feedbacks.filter(
                feedback_type="Appreciation"
            ).count()

        )

    # ==========================================================
    # CATEGORY CHART
    # ==========================================================

    category_data = (

        feedbacks

        .values("category")

        .annotate(total=Count("id"))

        .order_by("-total")

    )

    # ==========================================================
    # TOP CUSTOMERS
    # ==========================================================

    top_customers = (

        feedbacks

        .values("customer_name")

        .annotate(total=Count("id"))

        .order_by("-total")[:10]

    )

    # ==========================================================
    # RECENT FEEDBACK
    # ==========================================================

    recent_feedback = (

        feedbacks

        .order_by("-id")[:5]

    )

    # ==========================================================
    # SATISFACTION SCORES
    # ==========================================================

    satisfaction_data = {

        "overall": 4.24,

        "product_quality": 4.32,

        "delivery": 4.18,

        "communication": 4.26,

        "support": 4.21,

    }

    # ==========================================================
    # CONTEXT
    # ==========================================================

    context = {

        # KPI

        "total_feedback": total_feedback,

        "open_feedback": open_feedback,

        "overdue_feedback": overdue_feedback,

        "critical_feedback": critical_feedback,

        "avg_closure_days": avg_closure_days,

        # Charts

        "monthly_total": monthly_total,

        "monthly_complaints": monthly_complaints,

        "monthly_suggestions": monthly_suggestions,

        "monthly_appreciations": monthly_appreciations,

        "category_data": category_data,

        "top_customers": top_customers,

        # Tables

        "recent_feedback": recent_feedback,

        # Score Cards

        "satisfaction_data": satisfaction_data,

        # Misc

        "current_year": current_year,

    }

    return render(

        request,

        "feedback/feedback_dashboard.html",

        context

    )