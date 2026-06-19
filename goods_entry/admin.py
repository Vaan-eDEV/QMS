from django.contrib import admin

from .models import (
    ProductCategory,
    Product,
    GoodsBatch,
    GoodsItem,
    Inventory,
    InventoryTransaction,
    MaterialIssue
)

# =========================================================
# PRODUCT CATEGORY
# =========================================================

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


# =========================================================
# PRODUCT MASTER
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "product_code",
        "product_name",
        "category",
        "unit",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "product_code",
        "product_name",
        "category__name",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# GOODS ITEM INLINE
# =========================================================

class GoodsItemInline(admin.TabularInline):

    model = GoodsItem

    extra = 0

    readonly_fields = (
        "product",
        "product_code",
        "product_name",
        "quantity",
        "price",
    )


# =========================================================
# GOODS BATCH
# =========================================================

@admin.register(GoodsBatch)
class GoodsBatchAdmin(admin.ModelAdmin):

    list_display = (
        "batch_id",
        "po_reference",
        "from_location",
        "to_location",
        "status",
        "created_by",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "batch_id",
        "po_reference",
        "from_location",
        "to_location",
    )

    readonly_fields = (
        "created_at",
        "confirmed_at",
    )

    inlines = [
        GoodsItemInline
    ]


# =========================================================
# GOODS ITEM
# =========================================================

@admin.register(GoodsItem)
class GoodsItemAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "product_code",
        "product_name",
        "quantity",
        "price",
        "batch",
    )

    search_fields = (
        "product_code",
        "product_name",
        "product__product_name",
        "product__product_code",
        "batch__batch_id",
    )

    list_filter = (
        "product__category",
    )


# =========================================================
# INVENTORY
# =========================================================

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "product_code",
        "product_name",
        "stock_qty",
        "updated_at",
    )

    fields = (
        "product",
        "product_code",
        "product_name",
        "stock_qty",
        "updated_at",
    )

    search_fields = (
        "product_code",
        "product_name",
        "product__product_name",
        "product__product_code",
    )

    list_filter = (
        "product__category",
    )

    readonly_fields = (
        "updated_at",
    )

    autocomplete_fields = (
        "product",
    )

# =========================================================
# INVENTORY TRANSACTION
# =========================================================

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):

    list_display = (
        "product_code",
        "product_name",
        "quantity",
        "transaction_type",
        "reference_no",
        "created_by",
        "created_at",
    )

    list_filter = (
        "transaction_type",
        "created_at",
    )

    search_fields = (
        "product_code",
        "product_name",
        "reference_no",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# MATERIAL ISSUE
# =========================================================

@admin.register(MaterialIssue)
class MaterialIssueAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "product_code",
        "product_name",
        "issued_qty",
        "workorder_item",
        "issued_by",
        "issued_at",
    )

    list_filter = (
        "issued_at",
        "product__category",
    )

    search_fields = (
        "product_code",
        "product_name",
        "product__product_name",
        "product__product_code",
        "workorder_item__product_code",
        "workorder_item__work_order__wo_number",
    )

    readonly_fields = (
        "issued_at",
    )