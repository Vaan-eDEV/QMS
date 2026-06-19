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
    path("msa/<int:study_id>/add-reading/",views.msa_add_reading,name="msa_add_reading"),
]