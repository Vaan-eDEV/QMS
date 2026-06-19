from django.urls import path
from . import views

urlpatterns = [

    # =====================================================
    # GOODS ENTRY
    # =====================================================

    path("",views.goods_entry_page,name="goods_entry"),

    path("save/",views.save_goods_entry,name="save_goods_entry"),

    path("api/",views.goods_api,name="goods_api"),

    # =====================================================
    # RECEIVABLE / INWARD
    # =====================================================

    path("receivable/",views.receivable_page,name="receivable_page"),

    path("get-po-items/",views.get_po_items,name="get_po_items"),

    path("inward-po/",views.inward_po,name="inward_po"),

    # =====================================================
    # BATCH DETAILS
    # =====================================================

    path("batch/<str:batch_id>/",views.get_batch_details,name="get_batch_details"),

    path("confirm/<str:batch_id>/",views.confirm_batch,name="confirm_batch"),

    path("inventory-dashboard/",views.inventory_dashboard,name="inventory_dashboard"),

    path("inward-detail/",views.inward_detail,name="inward_detail"),

    path("material-issue/",views.material_issue_page,name="material_issue"),

    path("get-workorder-items/",views.get_workorder_items,name="get_workorder_items"),

    path("issue-material/",views.issue_material,name="issue_material"),
    # =====================================================
    # CATEGORY MASTER AJAX
    # =====================================================

    path(
        "get-categories/",
        views.get_categories,
        name="get_categories"
    ),

    path(
        "create-category/",
        views.create_category,
        name="create_category"
    ),
]