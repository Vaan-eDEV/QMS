from django.urls import path
from . import views

app_name = "po_qu"

urlpatterns = [

    # ================= COMBINED PAGE =================
    path('po-au/', views.po_au_view, name='po_au'),
    # ================= PURCHASE ORDER =================
    path('create/', views.create_po, name='create_po'),
    path('', views.po_list, name='po_list'),
    path("po/<int:po_id>/edit/", views.edit_po, name="edit_po"),
    path('<int:po_id>/', views.po_detail, name='po_detail'),
    path('po/<int:po_id>/pdf/', views.generate_po_pdf, name='po_pdf'),
    # ================= QUOTATION =================
    path('quotation/create/', views.create_quotation, name='create_quotation'),
    path('quotation/', views.quotation_list, name='quotation_list'),
    path("quotation/<int:quotation_id>/edit/", views.edit_quotation, name="edit_quotation"),
    path('quotation/<int:quotation_id>/', views.quotation_detail, name='quotation_detail'),
    path("quotation/<int:quotation_id>/pdf/", views.generate_quotation_pdf, name="quotation_pdf"),
    # ================= DELIVERY CHALLAN =================
    path('dc/create/', views.create_dc, name='create_dc'),
    path('dc/', views.dc_list, name='dc_list'),
    path("dc/<int:dc_id>/edit/", views.edit_dc, name="edit_dc"),
    path('dc/<int:dc_id>/', views.dc_detail, name='dc_detail'),
    path("dc/<int:dc_id>/pdf/", views.generate_dc_pdf, name="dc_pdf"),
    # ============================ verify signature ====================
    path('sign/', views.apply_signature, name='apply_signature'),
    # ====================== work order ==========================
    path('workorder/create/', views.create_workorder, name='create_workorder'),
    path('workorder/', views.workorder_list, name="workorer_list"),
    path('workorder/<int:wo_id>/',views.workorder_detail, name="workorder_detail"),
    path('workorder/<int:wo_id>/edit/', views.edit_workorder, name='edit_workorder'),
    path('workorder/<int:wo_id>/pdf/', views.generate_workorder_pdf, name="workorder_pdf"),
    # =========================== RFQ =============================
    path("rfq/create/",views.create_rfq,name="create_rfq"),
    path("rfq/",views.rfq_list,name="rfq_list"),
    path("rfq/<int:rfq_id>/",views.rfq_detail,name="rfq_detail"),
    path("rfq/<int:rfq_id>/edit/",views.edit_rfq,name="edit_rfq"),
]