from django.urls import path
from . import views

urlpatterns = [

    # ==========================
    # ========= Auth ===========
    # ==========================
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path("change-password/",views.change_password,name="change_password"),
    path('dashboard/', views.dashboard, name='main_dashboard'),
    # ==========================
    # ======== Documents =======
    # ==========================

    path('denied/', views.denied, name='denied'),
    path('sop/', views.sop, name='sop'),

    path("documents/upload/", views.upload_document, name="upload_document"),
    path("documents/<int:doc_id>/view/", views.view_document, name="view_document"),
    path("documents/save/<int:doc_id>/", views.save_document, name="save_document"),
    path("workflow/", views.document_workflow, name="document_workflow"),
    path("update-document-status/<int:doc_id>/", views.update_document_status, name="update_document_status"),
    path("finalize-document/<int:doc_id>/", views.finalize_document, name="finalize_document"),
    path('document/<int:doc_id>/edit/', views.edit_document, name='edit_document'),
    path("documents/<int:doc_id>/delete/", views.delete_document, name="delete_document"),
    path('documents/', views.document_home, name='document_home'),
    path('documents/folder/view/<int:folder_id>/', views.folder_documents, name='folder_documents'),
    path('documents/folder/<int:folder_id>/', views.document_home, name='document_home_folder'),
    path('documents/create-folder/', views.create_folder, name='create_folder'),
    path('documents/<int:doc_id>/delete', views.delete_documents, name='delete_documents'),
    path('documents/delete-folder/<int:id>/', views.delete_folder, name='delete_folder'),
    path('documents/verify-sign/', views.verify_signature_password, name='verify_signature_password'),
    path("documents/<int:doc_id>/sign/", views.sign_document, name="sign_document"),
    path("workflow-data/", views.workflow_data),
    path("workflow-notifications/", views.workflow_notifications),
    path("users-list/", views.users_list, name="users_list"),
    path("mark-as-read/<int:doc_id>/", views.mark_as_read),
    path('send-back/<int:doc_id>/', views.send_back, name='send_back'),
    path('revise-document/<int:doc_id>/', views.revise_document, name='revise_document'),
    path("archive/", views.archive_list, name="archive_list"),
    path("archive/view/<str:filename>/", views.view_archive_document, name="view_archive_document"),
    path("signed-pdf/<int:doc_id>/", views.render_signed_pdf, name="signed_pdf"),
    # ==========================
    # ========== Forms =========
    # ==========================
    path('forms/', views.form_list, name='form_list'),
    path('forms/folder/<int:folder_id>/', views.form_list, name='form_list_folder'),
    path("forms/create-folder/", views.create_form_folder, name="create_form_folder"),
    path('forms/create/', views.create_form, name='form_create'),
    path("forms/create/<int:folder_id>/", views.create_form, name="form_create_in_folder"),
    path('form/<int:form_id>/edit/', views.edit_form, name='edit_form'),
    path('form/<int:form_id>/delete/', views.delete_form, name='delete_form'),
    path('forms/<int:form_id>/add_stage/', views.add_stage, name='add_stage'),
    path("stage/<int:stage_id>/edit/", views.edit_stage, name="edit_stage"),
    path('projects/stage/<int:stage_id>/delete/', views.delete_stage, name='delete_stage'),
    path('stages/<int:stage_id>/add_field/', views.add_field, name='add_field'),
    path("field/<int:field_id>/edit/", views.edit_field, name="edit_field"),
    path("field/<int:field_id>/delete/", views.delete_field, name="delete_field"),
    # ==========================
    # ==== Multi-Stage Flow ====
    # ==========================
    path("forms/<int:form_id>/start/",views.start_form,name="start_form"),
    path("forms/<int:form_id>/stage/<int:stage_id>/<int:part_id>/",views.fill_stage,name="fill_stage"),
    path("forms/<int:form_id>/continue/<int:part_id>/",views.continue_to_next_form,name="continue_to_next_form"),
    path("forms/<int:form_id>/kanban/",views.kanban_board,name="kanban_board"),
    path("kanban/move/",views.move_kanban_card,name="move_kanban_card"),
    path("kanban/delete/",views.delete_form_batch,name="delete_form_batch"),
    path("forms/<int:form_id>/complete/",views.form_complete,name="form_complete"),
    path("tracker/search/",views.tracker_search,name="tracker_search"),
    path("forms/folder/delete/<int:folder_id>/",views.delete_form_folder,name="delete_form_folder"),
    # ===========================
    # ===== Submitted Forms =====
    # ===========================
    path('submitted-forms/',views.submitted_forms_list,name='submitted_forms_list'),
    path("submitted-forms/<str:flow_id>/parts/",views.submitted_parts_list,name="submitted_parts_list"),
    path("submitted-forms/part/<int:part_id>/",views.submitted_part_detail,name="submitted_part_detail"),
    path('submitted-forms/delete/<uuid:flow_id>/',views.delete_submission,name='delete_submission'),
    # ==========================
    # ========== APIs ==========
    # ==========================
    path('api/form/<int:form_id>/stages/',views.api_form_stages),
    path('api/stage/<int:stage_id>/fields/',views.api_stage_fields,name='api_stage_fields'),
    path("verify-signature/",views.verify_signature,name="verify_signature"),
    path("workflows/",views.workflow_list,name="workflow_list"),
    path('flow/kanban/',views.flow_kanban,name='flow_kanban'),
    path("settings/page-access/", views.page_settings, name="page_settings"),
    path("unlock-user/<int:user_id>/", views.unlock_user, name="unlock_user"),
    path("materials/", views.material_batches, name="material_batches"),
    path("work-trace/", views.user_work_trace, name="user_work_trace"),
    path("audit/part/<int:part_id>/",views.part_audit_logs,name="part_audit_logs"),
    # ==========================
    # ========== CAPA ==========
    # ==========================
    path("capa/", views.capa_list, name="capa_list"),
    path("capa/new/", views.capa_create, name="capa_create"),
    path("capa/<int:pk>/", views.capa_detail, name="capa_detail"),
    path("capa/update-status/", views.update_capa_status, name="update_capa_status"),
    # ==========================
    # ========== NCR ===========
    # ==========================
    path("move-to-ncr/", views.move_to_ncr, name="move_to_ncr"),
    path("ncr/<int:ncr_id>/create-capa/", views.create_capa_from_ncr, name="create_capa_from_ncr"),
    path("ncr/<int:ncr_id>/delete/", views.delete_ncr, name="delete_ncr"),
    
    
    path("machine/verify/", views.machine_verify),
    path("machine/start/", views.machine_start),
    path("machine/logout/", views.machine_logout, name="machine_logout"),
    path("machine/previous/", views.machine_previous),
    path("machine/check-session/", views.machine_check_session),
    path("machine/log/", views.machine_log),
    path("machine/dashboard/", views.machine_dashboard, name="machine_dashboard"),
    
    path("rfq-workorders/",views.rfq_to_workorder_list,name="rfq_to_workorder_list"),
    path("workorder/<int:wo_id>/kanban/",views.workorder_kanban,name="workorder_kanban"),
    path("workorders/",views.workorder_list,name="workorder_list"),
    path("workorder/item/<int:item_id>/forms/",views.stage_forms,name="stage_forms"),
    path("workorder/update-stage/",views.update_workorder_stage,name="update_workorder_stage"),
    path("workorder/form/start/<int:form_id>/<int:item_id>/",views.start_workorder_form,name="start_workorder_form"),
    path("workorder/<int:item_id>/create-rfq/",views.create_rfq_from_workorder,name="create_rfq_from_workorder"),
    path("workorder/assign-user/",views.assign_workorder_user,name="assign_workorder_user"),
    path("rfq/<int:rfq_id>/",views.rfq_detail,name="rfq_detail"),
    path("rfq/<int:rfq_id>/upload-attachment/",views.upload_rfq_attachment,name="upload_rfq_attachment"),
]   