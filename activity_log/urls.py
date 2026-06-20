from django.urls import path
from . import views

urlpatterns = [

    path("",views.activity_log_list,name="activity_log_list"),
    path("create/",views.activity_log_create,name="activity_log_create"),
    path("<int:pk>/",views.activity_log_detail,name="activity_log_detail"),
    path("<int:pk>/edit/",views.activity_log_edit,name="activity_log_edit"),
    path("<int:pk>/delete/",views.activity_log_delete,name="activity_log_delete"),
    path(
        "dashboard/",
        views.activity_dashboard,
        name="activity_dashboard"
    ),
    path(
        "api/<int:pk>/",
        views.activity_log_json,
        name="activity_log_json"
    ),
]