from django.urls import path
from . import views

urlpatterns = [

    # ======================================================
    # 🧪 TEST MODULE
    # ======================================================
    path("admin/test/create/", views.create_test, name="create_test"),
    path("admin/test/<int:test_id>/add/", views.add_question, name="add_question"),
    path("student/tests/", views.student_home, name="student_home"),
    path("list/", views.test_list, name="test_list"),
    path("student/test/<int:test_id>/", views.attempt_test, name="attempt_test"),

    path("results/", views.result_list, name="result_list"),
    path("results/<int:result_id>/", views.result_detail, name="result_detail"),

    path("delete/<int:test_id>/", views.delete_test, name="delete_test"),
    path("result-delete/<int:result_id>/", views.delete_result, name="delete_result"),

    # ======================================================
    # 📚 STUDY MATERIAL
    # ======================================================
    path("test/<int:test_id>/materials/", views.upload_material, name="upload_material"),
    path("test/<int:test_id>/study/", views.study_material_view, name="study_material_view"),
    path("material/complete/<int:material_id>/", views.mark_material_complete, name="mark_material_complete"),

    # ======================================================
    # 👨‍💼 EMPLOYEE MODULE
    # ======================================================

    # ---- BASIC ----
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/create/", views.create_employee, name="create_employee"),
    path("employees/view/<int:emp_id>/", views.employee_detail, name="employee_detail"),
    path("employees/edit/<int:emp_id>/", views.edit_employee, name="edit_employee"),

    # ---- CERTIFICATES ----
    path("employees/<int:emp_id>/upload/", views.add_certificate, name="add_certificate"),
    path("certificate/delete/<int:cert_id>/", views.delete_certificate, name="delete_certificate"),
    path("certificates/delete/<int:cert_id>/", views.delete_certificates, name="delete_certificates"),

    # ---- APPROVAL FLOW (IMPORTANT) ----
    path("employees/approval/", views.employee_approval_list, name="employee_approval_list"),

    # 🔥 THIS IS YOUR MAIN PAGE (VIEW + EDIT COMBINED)
    path(
        "employees/approval/<int:emp_id>/",
        views.employee_detail_approval,
        name="employee_detail_approval"
    ),

    path("employees/approve/<int:emp_id>/", views.approve_employee, name="approve_employee"),
    path("edit-test/<int:test_id>/",views.edit_test,name="edit_test"),
    path("edit-question/<int:question_id>/",views.edit_question,name="edit_question"),

    path("delete-question/<int:question_id>/",views.delete_question,name="delete_question"),
    # ---- DASHBOARD / PROFILE ----
    path("delete-material/<int:material_id>/",views.delete_material,name="delete_material"),
    path("employee/dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path("my-profile/", views.my_profile, name="my_profile"),

]