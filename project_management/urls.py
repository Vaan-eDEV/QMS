from django.urls import path
from . import views

urlpatterns = [

    # ---------- project ---------- 
    path("projects/",views.project_list,name="project_list"),
    path("project/create/",views.project_create,name="project_create"),
    path("project/<int:project_id>/kanban/",views.project_kanban,name="project_kanban"),
    path("project/<int:project_id>/delete/", views.project_delete, name="project_delete"),
    # ---------- Stage ----------
    path("update-task-stage/", views.update_task_stage, name="update_task_stage"),
    path("create-stage/", views.create_stage, name="create_stage"),
    path("stage/<int:stage_id>/delete/", views.delete_stage, name="delete_stage"),
    # ---------- Task -----------
    path("create-task/", views.create_task, name="create_task"),
    path("task/<int:task_id>/",views.task_detail,name="task_detail"),
    path("task/<int:task_id>/delete/", views. delete_task, name="delete_task"),


   
    

]