from django.contrib import admin

from .models import *

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):

    list_display = (
        "instrument_id",
        "name",
        "category",
        "status",
        "next_due",
    )

    search_fields = (
        "instrument_id",
        "name",
        "serial_no",
    )

    list_filter = (
        "category",
        "status",
    )


@admin.register(CalibrationRecord)
class CalibrationRecordAdmin(admin.ModelAdmin):

    list_display = (
        "instrument",
        "calibration_date",
        "next_due_date",
        "result",
    )

    list_filter = (
        "result",
        "calibration_date",
    )

    search_fields = (
        "certificate_number",
        "calibration_agency",
        "instrument__instrument_id",
    )


@admin.register(MSAStudy)
class MSAStudyAdmin(admin.ModelAdmin):

    list_display = (
        "msa_no",
        "instrument",
        "study_type",
        "part_number",
        "operator_count",
        "part_count",
        "trial_count",
        "grr_percentage",
        "study_status",
        "study_date",
    )

    list_filter = (
        "study_type",
        "study_status",
        "study_date",
    )

    search_fields = (
        "msa_no",
        "part_number",
        "instrument__instrument_id",
        "instrument__name",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(MSAReading)
class MSAReadingAdmin(admin.ModelAdmin):

    list_display = (
        "study",
        "operator",
        "part_no",
        "trial_no",
        "measured_value",
    )

    list_filter = (
        "operator",
        "study",
    )

    search_fields = (
        "operator",
        "part_no",
        "study__msa_no",
    )


class SPCReadingInline(admin.TabularInline):
    model = SPCReading
    extra = 0

@admin.register(SPCControlPlan)
class SPCControlPlanAdmin(admin.ModelAdmin):

    list_display = (
        "plan_no",
        "part_number",
        "characteristic",
        "instrument",
        "lsl",
        "target",
        "usl",
        "average",
    )

    search_fields = (
        "plan_no",
        "part_number",
        "characteristic",
    )

    inlines = [
        SPCReadingInline
    ]

@admin.register(SPCReading)
class SPCReadingAdmin(admin.ModelAdmin):

    list_display = (
        "control_plan",
        "sample_no",
        "measured_value",
        "reading_date",
    )

    search_fields = (
        "sample_no",
    )