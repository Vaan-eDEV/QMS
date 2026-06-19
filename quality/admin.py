from django.contrib import admin

from .models import (
    Instrument,
    CalibrationRecord,
    MSAStudy,
    MSAReading,
)


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