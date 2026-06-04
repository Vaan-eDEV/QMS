from django.urls import path
from . import views

urlpatterns = [

    path("builder/", views.form_builder, name="form_builder"),
    
    path("edit/<int:form_id>/", views.edit_form, name="edit_forms"),
    
    path("delete-column/<int:col_id>/", views.delete_column),

    path("list/", views.form_list, name="form_lists"),
    
    path("delete-form/<int:form_id>/", views.delete_form, name="delete_forms"),

    path("fill/<int:form_id>/", views.fill_form, name="fill_form"),

    path("save/<int:form_id>/", views.save_response, name="save_response"),
    
    path("delete-stage/<int:stage_id>/", views.delete_stage, name="delete_stages"),
    
    path("edit-response/<int:response_id>/", views.edit_response, name="edit_response"),

    path("responses/<int:form_id>/", views.responses, name="responses"),
    
    path("kanban/", views.kanban_view, name="kanban_view"),

    path("update-field/", views.update_field_position, name="update_field_position"),

    path("add-field/", views.add_field_ajax, name="add_field_ajax"),

    path("delete-field/<int:field_id>/", views.delete_field, name="delete_fields"),

    path("edit-field/<int:field_id>/", views.edit_field, name="edit_fields"),
    
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
    
    path("verify-signature/", views.verify_signature, name="verify_signature"),

    path("open-next-form/", views.open_next_form, name="open_next_form"),
    
    path("summary/<str:ref_id>/", views.process_summary, name="process_summary"),
    
    path("data/", views.data_list, name="data_list"),
    
    path("data/<str:ref_id>/", views.data_detail, name="data_detail"),
    
    path("company/<str:company>/", views.company_rfq_list),
    
    path("register/", views.register_list, name="register_list"),
    
    path("response-detail/<int:response_id>/", views.response_detail),
    
    path("register-data/", views.register_data_api),

    path('register-detail/<int:response_id>/', views.register_detail_api),

    path('costing-action/', views.costing_action, name='costing_action'),

    path("file-view/<path:path>/", views.open_uploaded_file, name="file_view"),

    path("delete-card/", views.delete_card, name="delete_card"),

    path("move-to-won/", views.move_to_won, name="move_to_won"),

    path("review-won/", views.review_won, name="review_won"),

    path("move-stage/", views.move_stage, name="move_stage"),

    path(
    "delete-table/<int:table_id>/",
    views.delete_table,
    name="delete_table"
),

]
