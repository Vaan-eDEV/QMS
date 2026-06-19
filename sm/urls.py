from django.urls import path
from . import views

urlpatterns = [

    # =====================================
    # EXISTING URLS
    # =====================================

    path(
        '',
        views.supplier_dashboard,
        name='sm_dashboard'
    ),

    path(
        'suppliers/',
        views.supplier_list,
        name='supplier_list'
    ),

    path(
        'create/',
        views.create_supplier,
        name='create_supplier'
    ),

    path(
        'supplier/<int:supplier_id>/',
        views.supplier_detail,
        name='supplier_detail'
    ),

    path(
        'stage/<int:stage_id>/update/',
        views.update_stage_status,
        name='update_stage_status'
    ),

    path(
        'supplier/<int:supplier_id>/upload-document/',
        views.upload_document,
        name='upload_document'
    ),

    path(
        'supplier/<int:supplier_id>/evaluation/',
        views.supplier_evaluation,
        name='supplier_evaluation'
    ),

    path(
        'supplier/<int:supplier_id>/risk/',
        views.risk_classification,
        name='risk_classification'
    ),

    path(
        'supplier/<int:supplier_id>/delete/',
        views.delete_supplier,
        name='delete_supplier'
    ),

    # =====================================
    # SUPPLIER AUDIT MODULE
    # =====================================

    path(
        'supplier-audits/',
        views.supplier_audit_list,
        name='supplier_audit_list'
    ),

    path(
        'supplier/<int:supplier_id>/audit/',
        views.supplier_audit_dashboard,
        name='supplier_audit_dashboard'
    ),

    path(
        'supplier/<int:supplier_id>/audit-request/',
        views.create_audit_request,
        name='create_audit_request'
    ),

]