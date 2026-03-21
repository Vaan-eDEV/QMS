from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import PurchaseRequisitionViewSet, QMSProcessViewSet, QMSStageAttachmentViewSet

router = DefaultRouter()
router.register("processes", QMSProcessViewSet, basename="processes")
router.register("purchase-requests", PurchaseRequisitionViewSet, basename="purchase-requests")
router.register("attachments", QMSStageAttachmentViewSet, basename="attachments")

urlpatterns = [
    path("", include(router.urls)),
]
