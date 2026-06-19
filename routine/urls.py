from django.urls import path
from . import views

app_name = "routine"

urlpatterns = [

    # Dashboard
    path("",views.routine_dashboard,name="dashboard"),

    # Category
    path("categories/",views.routine_category_list,name="category_list"),

    path("categories/create/",views.create_category,name="create_category"),

    path("routines/create/",views.create_routine,name="create_routine"),

    path("routines/",views.routine_list,name="routine_list"),

    # =========================================================
    # CHECKLIST ITEMS
    # =========================================================

    path("routine/<int:routine_id>/checklist/",views.checklist_item_list,name="checklist_item_list"),

    path("routine/<int:routine_id>/checklist/create/",views.create_checklist_item,name="create_checklist_item"),

    path("checklist/<int:item_id>/edit/",views.edit_checklist_item,name="edit_checklist_item"),

    path("checklist/<int:item_id>/delete/",views.delete_checklist_item,name="delete_checklist_item"),

    # =====================================================
    # CHECKLIST
    # =====================================================

    path("routine/<int:routine_id>/checklist/",views.checklist_item_list,
    name="checklist_item_list"
),

path(
    "checklist-records/",
    views.checklist_records,
    name="checklist_records"
),

path(
    "schedule/<int:routine_id>/",
    views.schedule_routine,
    name="schedule_routine"
),

path(
    "my-checklists/",
    views.my_checklists,
    name="my_checklists"
)
]