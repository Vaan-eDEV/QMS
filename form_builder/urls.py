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
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path("verify-signature/", views.verify_signature, name="verify_signature"),

]