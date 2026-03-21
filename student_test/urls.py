from django.urls import path
from . import views

urlpatterns = [
    
    path("admin/test/create/", views.create_test, name="create_test"),
    path("admin/test/<int:test_id>/add/", views.add_question, name="add_question"),
    path("student/tests/", views.student_home, name="student_home"),
    path("list/", views.test_list, name="test_list"),
    path("student/test/<int:test_id>/", views.attempt_test, name="attempt_test"),
    path("results/", views.result_list, name="result_list"),
    path("results/<int:result_id>/", views.result_detail, name="result_detail"),

    # ========================== Delete Options urls ==========================
    path("delete/<int:test_id>/", views.delete_test, name="delete_test"),
    path("result-delete/<int:result_id>/", views.delete_result, name="delete_result"),


]
