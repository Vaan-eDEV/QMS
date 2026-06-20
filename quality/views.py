from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *

# =====================================================
# DASHBOARD
# =====================================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import (
    Instrument,
    CalibrationRecord
)


@login_required
def quality_dashboard(request):

    instruments = Instrument.objects.all()

    total_instruments = instruments.count()

    overdue_count = 0
    due_count = 0

    for instrument in instruments:

        if instrument.is_overdue:

            overdue_count += 1

        elif (
            instrument.days_to_due is not None
            and instrument.days_to_due <= 30
        ):

            due_count += 1

    calibration_count = (
        CalibrationRecord.objects.count()
    )

    recent_calibrations = (
        CalibrationRecord.objects
        .select_related("instrument")
        .order_by("-calibration_date")[:10]
    )

    context = {

        "total_instruments": total_instruments,

        "overdue_count": overdue_count,

        "due_count": due_count,

        "calibration_count": calibration_count,

        "recent_calibrations": recent_calibrations,
    }

    return render(
        request,
        "quality/quality_dashboard.html",
        context
    )

# =====================================================
# INSTRUMENTS
# =====================================================

@login_required
def instrument_list(request):

    instruments = Instrument.objects.all().order_by(
        "instrument_id"
    )

    return render(
        request,
        "quality/instrumental_list.html",
        {
            "instruments": instruments
        }
    )


@login_required
def instrument_create(request):

    if request.method == "POST":

        Instrument.objects.create(

            instrument_id=request.POST.get(
                "instrument_id"
            ),

            name=request.POST.get(
                "name"
            ),

            category=request.POST.get(
                "category"
            ),

            manufacturer=request.POST.get(
                "manufacturer"
            ),

            model_no=request.POST.get(
                "model_no"
            ),

            serial_no=request.POST.get(
                "serial_no"
            ),

            location=request.POST.get(
                "location"
            ),

            purchase_date=request.POST.get(
                "purchase_date"
            ) or None,

            range_specification=request.POST.get(
                "range_specification"
            ),

            accuracy=request.POST.get(
                "accuracy"
            ),

            calibration_frequency_days=request.POST.get(
                "calibration_frequency_days"
            ) or 365,
        )

        messages.success(
            request,
            "Instrument created successfully."
        )

        return redirect(
            "instrument_list"
        )

    return render(
        request,
        "quality/instrument_create.html"
    )


@login_required
def instrument_edit(request, pk):

    instrument = get_object_or_404(
        Instrument,
        pk=pk
    )

    if request.method == "POST":

        instrument.instrument_id = request.POST.get(
            "instrument_id"
        )

        instrument.name = request.POST.get(
            "name"
        )

        instrument.category = request.POST.get(
            "category"
        )

        instrument.manufacturer = request.POST.get(
            "manufacturer"
        )

        instrument.model_no = request.POST.get(
            "model_no"
        )

        instrument.serial_no = request.POST.get(
            "serial_no"
        )

        instrument.location = request.POST.get(
            "location"
        )

        instrument.purchase_date = request.POST.get(
            "purchase_date"
        ) or None

        instrument.range_specification = request.POST.get(
            "range_specification"
        )

        instrument.accuracy = request.POST.get(
            "accuracy"
        )

        instrument.calibration_frequency_days = (
            request.POST.get(
                "calibration_frequency_days"
            ) or 365
        )

        instrument.save()

        messages.success(
            request,
            "Instrument updated successfully."
        )

        return redirect(
            "instrument_list"
        )

    return render(
        request,
        "quality/instrument_edit.html",
        {
            "instrument": instrument
        }
    )


@login_required
def instrument_delete(request, pk):

    instrument = get_object_or_404(
        Instrument,
        pk=pk
    )

    instrument.delete()

    messages.success(
        request,
        "Instrument deleted successfully."
    )

    return redirect(
        "instrument_list"
    )


# =====================================================
# CALIBRATION
# =====================================================

@login_required
def calibration_list(request):

    calibrations = (
        CalibrationRecord.objects
        .select_related("instrument")
        .order_by("-calibration_date")
    )

    return render(
        request,
        "quality/calibration_list.html",
        {
            "calibrations": calibrations
        }
    )


@login_required
def calibration_create(request):

    instruments = Instrument.objects.all()

    if request.method == "POST":

        instrument = get_object_or_404(
            Instrument,
            pk=request.POST.get("instrument")
        )

        CalibrationRecord.objects.create(

            instrument=instrument,

            calibration_date=request.POST.get(
                "calibration_date"
            ),

            next_due_date=request.POST.get(
                "next_due_date"
            ),

            certificate_number=request.POST.get(
                "certificate_number"
            ),

            calibration_agency=request.POST.get(
                "calibration_agency"
            ),

            result=request.POST.get(
                "result"
            ),

            remarks=request.POST.get(
                "remarks"
            ),

            certificate_file=request.FILES.get(
                "certificate_file"
            ),

            created_by=request.user
        )

        messages.success(
            request,
            "Calibration record created successfully."
        )

        return redirect(
            "calibration_list"
        )

    return render(
        request,
        "quality/calibration_create.html",
        {
            "instruments": instruments
        }
    )


@login_required
def calibration_history(request, instrument_id):

    instrument = get_object_or_404(
        Instrument,
        pk=instrument_id
    )

    calibrations = (
        CalibrationRecord.objects
        .filter(instrument=instrument)
        .order_by("-calibration_date")
    )

    return render(
        request,
        "quality/calibration_history.html",
        {
            "instrument": instrument,
            "calibrations": calibrations
        }
    )


@login_required
def msa_dashboard(request):

    study_count = (
        MSAStudy.objects.count()
    )

    reading_count = (
        MSAReading.objects.count()
    )

    grr_count = (
        MSAStudy.objects.filter(
            study_type="GRR"
        ).count()
    )

    bias_count = (
        MSAStudy.objects.filter(
            study_type="BIAS"
        ).count()
    )

    linearity_count = (
        MSAStudy.objects.filter(
            study_type="LINEARITY"
        ).count()
    )

    stability_count = (
        MSAStudy.objects.filter(
            study_type="STABILITY"
        ).count()
    )

    instrument_count = (
        Instrument.objects.count()
    )

    recent_studies = (
        MSAStudy.objects
        .select_related("instrument")
        .order_by("-study_date")[:10]
    )

    context = {

        "study_count": study_count,

        "reading_count": reading_count,

        "grr_count": grr_count,

        "bias_count": bias_count,

        "linearity_count": linearity_count,

        "stability_count": stability_count,

        "instrument_count": instrument_count,

        "recent_studies": recent_studies,
    }

    return render(
        request,
        "quality/msa/msa_dashboard.html",
        context
    )




@login_required
def msa_list(request):

    studies = (
        MSAStudy.objects
        .select_related("instrument")
        .order_by("-study_date")
    )

    instruments = Instrument.objects.all()

    return render(
        request,
        "quality/msa/msa_list.html",
        {
            "studies": studies,
            "instruments": instruments,
        }
    )




from django.contrib import messages
from django.shortcuts import redirect, render

@login_required
def msa_create(request):

    if request.method == "POST":

        MSAStudy.objects.create(

            msa_no=request.POST.get(
                "msa_no"
            ),

            instrument_id=request.POST.get(
                "instrument"
            ),

            study_type=request.POST.get(
                "study_type"
            ),

            part_number=request.POST.get(
                "part_number"
            ),

            operator_count=request.POST.get(
                "operator_count"
            ) or 3,

            part_count=request.POST.get(
                "part_count"
            ) or 10,

            trial_count=request.POST.get(
                "trial_count"
            ) or 3,

            study_date=request.POST.get(
                "study_date"
            ),

            remarks=request.POST.get(
                "remarks"
            ),

            study_status="PENDING",

            created_by=request.user
        )

        messages.success(
            request,
            "MSA Study created successfully."
        )

        return redirect(
            "msa_list"
        )

    return redirect(
        "msa_list"
    )

@login_required
def msa_detail(
    request,
    study_id
):

    study = get_object_or_404(
        MSAStudy,
        id=study_id
    )

    readings = (
        study.readings.all()
        .order_by(
            "operator",
            "part_no",
            "trial_no"
        )
    )

    return render(
        request,
        "quality/msa/msa_detail.html",
        {
            "study": study,
            "readings": readings
        }
    )





from statistics import stdev


def calculate_grr(study):

    readings = list(
        study.readings.values_list(
            "measured_value",
            flat=True
        )
    )

    if len(readings) < 2:

        study.grr_percentage = None
        study.study_status = "PENDING"
        study.save()

        return

    values = [
        float(x)
        for x in readings
    ]

    total_variation = stdev(values)

    if total_variation == 0:

        grr = 0

    else:

        gauge_variation = (
            total_variation * 0.20
        )

        grr = (
            gauge_variation /
            total_variation
        ) * 100

    study.grr_percentage = round(
        grr,
        2
    )

    if grr < 10:

        study.study_status = "ACCEPTED"

    elif grr <= 30:

        study.study_status = "CONDITIONAL"

    else:

        study.study_status = "REJECTED"

    study.save()




@login_required
def msa_add_reading(
    request,
    study_id
):

    study = get_object_or_404(
        MSAStudy,
        id=study_id
    )

    if request.method == "POST":

        MSAReading.objects.create(

            study=study,

            operator=request.POST.get(
                "operator"
            ),

            part_no=request.POST.get(
                "part_no"
            ),

            trial_no=request.POST.get(
                "trial_no"
            ),

            measured_value=request.POST.get(
                "measured_value"
            )
        )
        calculate_grr(
            study
        )

        return redirect(
            "msa_add_reading",
            study.id
        )

    return render(
        request,
        "quality/msa/msa_add_reading.html",
        {
            "study": study
        }
    )




# =============================================================================================
# ============================================== SPC ==========================================
# =============================================================================================
@login_required
def spc_dashboard(request):

    plans = (
        SPCControlPlan.objects
        .select_related("instrument")
        .order_by("-created_at")
    )

    plan_count = plans.count()

    reading_count = (
        SPCReading.objects.count()
    )

    recent_plans = plans[:10]

    cp_values = []

    cpk_values = []

    for plan in plans:

        if plan.cp is not None:
            cp_values.append(
                float(plan.cp)
            )

        if plan.cpk is not None:
            cpk_values.append(
                float(plan.cpk)
            )

    average_cp = None

    if cp_values:

        average_cp = round(
            sum(cp_values)
            /
            len(cp_values),
            2
        )

    average_cpk = None

    if cpk_values:

        average_cpk = round(
            sum(cpk_values)
            /
            len(cpk_values),
            2
        )

    context = {

        "plan_count": plan_count,

        "reading_count": reading_count,

        "average_cp": average_cp,

        "average_cpk": average_cpk,

        "recent_plans": recent_plans,
    }

    return render(
        request,
        "quality/spc/spc_dashboard.html",
        context
    )
@login_required
def spc_list(request):

    plans = (
        SPCControlPlan.objects
        .select_related("instrument")
        .order_by("-created_at")
    )

    instruments = (
        Instrument.objects.all()
    )

    return render(
        request,
        "quality/spc/spc_list.html",
        {
            "plans": plans,
            "instruments": instruments,
        }
    ) 

@login_required
def spc_create(request):

    if request.method == "POST":

        SPCControlPlan.objects.create(

            plan_no=request.POST.get(
                "plan_no"
            ),

            part_number=request.POST.get(
                "part_number"
            ),

            characteristic=request.POST.get(
                "characteristic"
            ),

            instrument_id=request.POST.get(
                "instrument"
            ),

            lsl=request.POST.get(
                "lsl"
            ),

            target=request.POST.get(
                "target"
            ),

            usl=request.POST.get(
                "usl"
            ),

            sample_size=request.POST.get(
                "sample_size"
            ) or 5,

            frequency=request.POST.get(
                "frequency"
            ),

            created_by=request.user
        )

        messages.success(
            request,
            "SPC Control Plan created successfully."
        )

        return redirect(
            "spc_list"
        )

    return redirect(
        "spc_list"
    )


@login_required
def spc_detail(
    request,
    plan_id
):

    plan = get_object_or_404(
        SPCControlPlan,
        id=plan_id
    )

    readings = (
        plan.readings.all()
        .order_by("-reading_date")
    )

    return render(
        request,
        "quality/spc/spc_detail.html",
        {
            "plan": plan,
            "readings": readings,
        }
    )


@login_required
def spc_add_reading(
    request,
    plan_id
):

    plan = get_object_or_404(
        SPCControlPlan,
        id=plan_id
    )

    if request.method == "POST":

        SPCReading.objects.create(

            control_plan=plan,

            sample_no=request.POST.get(
                "sample_no"
            ),

            measured_value=request.POST.get(
                "measured_value"
            ),

            recorded_by=request.user
        )

        messages.success(
            request,
            "Reading added successfully."
        )

        return redirect(
            "spc_add_reading",
            plan.id
        )

    return render(
        request,
        "quality/spc/spc_add_reading.html",
        {
            "plan": plan
        }
    )  


@login_required
def spc_delete_reading(
    request,
    reading_id
):

    reading = get_object_or_404(
        SPCReading,
        id=reading_id
    )

    plan_id = (
        reading.control_plan.id
    )

    reading.delete()

    messages.success(
        request,
        "Reading deleted successfully."
    )

    return redirect(
        "spc_add_reading",
        plan_id
    )