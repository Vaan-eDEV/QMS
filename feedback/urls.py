
from django.urls import path

from .views import (
    feedback_list,
    feedback_form,
    feedback_detail,
    delete_feedback,
    update_feedback_status,
    edit_feedback,
    feedback_dashboard
)

urlpatterns = [

    path('',feedback_list,name='feedback_list'),
    path('new/',feedback_form,name='feedback_form'),
    path('detail/<int:id>/',feedback_detail,name='feedback_detail'),
    path('delete/<int:id>/',delete_feedback,name='delete_feedback'),
    path('update-status/<int:id>/',update_feedback_status,name='update_feedback_status'),
    path('edit/<int:id>/',edit_feedback,name='edit_feedback'),
    path('dashboard/',feedback_dashboard,name='feedback_dashboard'),

]

