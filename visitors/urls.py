from django.urls import path
from . import views

app_name = "visitors"

urlpatterns = [

    path(
        "",
        views.visitor_dashboard,
        name="visitor_dashboard"
    ),

    path(
        "create/",
        views.create_visitor,
        name="create_visitor"
    ),

    path(
        "<int:visitor_id>/",
        views.visitor_detail,
        name="visitor_detail"
    ),

    path(
        "<int:visitor_id>/checkout/",
        views.checkout_visitor,
        name="checkout_visitor"
    ),

    path(

    "<int:visitor_id>/pass/",

    views.visitor_pass,

    name="visitor_pass"

),

]