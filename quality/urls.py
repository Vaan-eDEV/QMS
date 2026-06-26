from django.urls import path

from . import views

urlpatterns = [

    # =====================================
    # DASHBOARD
    # =====================================
    path("",views.quality_dashboard,name="quality_dashboard"),
    # =====================================
    # INSTRUMENTS
    # =====================================
    path("instruments/",views.instrument_list,name="instrument_list"),
    path("instruments/create/",views.instrument_create,name="instrument_create"),
    path("instruments/<int:pk>/edit/",views.instrument_edit,name="instrument_edit"),
    path("instruments/<int:pk>/delete/",views.instrument_delete,name="instrument_delete"),
    # =====================================
    # CALIBRATION
    # =====================================
    path("calibrations/",views.calibration_list,name="calibration_list"),
    path("calibrations/create/",views.calibration_create,name="calibration_create"),
    path("calibrations/history/<int:instrument_id>/",views.calibration_history,name="calibration_history"),
    # =====================================
    # MSA
    # =====================================
    path("msa/",views.msa_list,name="msa_list"),
    path("msa/dashboard/",views.msa_dashboard,name="msa_dashboard"),
    path("msa/create/",views.msa_create,name="msa_create"),
    path("msa/<int:study_id>/",views.msa_detail,name="msa_detail"),
    path("msa/<int:study_id>/sheet/",views.msa_reading_sheet,name="msa_reading_sheet"),
    # ==========================================
    # SPC MODULE
    # ==========================================
    path("spc/",views.spc_dashboard,name="spc_dashboard"),
    path("spc/list/",views.spc_list,name="spc_list"),
    path("spc/create/",views.spc_create,name="spc_create"),
    path("spc/<int:plan_id>/",views.spc_detail,name="spc_detail"),
    path("spc/<int:plan_id>/add-reading/",views.spc_add_reading,name="spc_add_reading"),
    path("spc/reading/<int:reading_id>/delete/",views.spc_delete_reading,name="spc_delete_reading"),



]