from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem,Quotation,QuotationItem,DeliveryChallan,DeliveryChallanItem,WorkOrder,RFQ,WorkOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier_name', 'date', 'grand_total', 'status']
    inlines = [PurchaseOrderItemInline]
    
admin.site.register(Quotation)

admin.site.register(QuotationItem)

admin.site.register(DeliveryChallan)

admin.site.register(DeliveryChallanItem)

admin.site.register(WorkOrder)

admin.site.register(WorkOrderItem)

admin.site.register(RFQ)