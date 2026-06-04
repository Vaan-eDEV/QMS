from django.urls import path

from . import views


urlpatterns = [

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
        'supplier/<int:supplier_id>/delete/',
        views.delete_supplier,
        name='delete_supplier'
    ),

]