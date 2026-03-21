from django.urls import path
from . import views

urlpatterns = [
    path("", views.goods_entry_page, name="goods_entry"),
    path("save/", views.save_goods_entry, name="save_goods_entry"),
    path("api/", views.goods_api, name="goods_api"),
    path("receivable/", views.receivable_page, name="receivable_page"),
    path("batch/<str:batch_id>/", views.get_batch_details, name="get_batch_details"),
    path("confirm/<str:batch_id>/", views.confirm_batch, name="confirm_batch"),

]
