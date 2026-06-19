from django.contrib import admin

from .models import (
    RoutineCategory,
    RoutineMaster,
    RoutineChecklistItem,
    RoutineSchedule,
    RoutineExecution,
    RoutineResponse,
    RoutineAttachment,
    RoutinePhoto,
    RoutineActivity,
    RoutineNCR,
)


# =====================================================
# INLINE MODELS
# =====================================================

class RoutineChecklistItemInline(
    admin.TabularInline
):
    model = RoutineChecklistItem
    extra = 0


class RoutineResponseInline(
    admin.TabularInline
):
    model = RoutineResponse
    extra = 0
    readonly_fields = (
        "submitted_at",
    )


class RoutineActivityInline(
    admin.TabularInline
):
    model = RoutineActivity
    extra = 0
    readonly_fields = (
        "performed_at",
    )


# =====================================================
# CATEGORY
# =====================================================

@admin.register(RoutineCategory)
class RoutineCategoryAdmin(
    admin.ModelAdmin
):

    list_display = (
        "category_name",
        "is_active",
        "created_by",
        "created_at",
    )

    search_fields = (
        "category_name",
        "description",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = (
        "category_name",
    )


# =====================================================
# ROUTINE MASTER
# =====================================================

@admin.register(RoutineMaster)
class RoutineMasterAdmin(
    admin.ModelAdmin
):

    list_display = (
        "routine_no",
        "routine_name",
        "category",
        "department",
        "location",
        "status",
        "critical_routine",
        "created_at",
    )

    search_fields = (
        "routine_no",
        "routine_name",
        "department",
        "location",
    )

    list_filter = (
        "status",
        "critical_routine",
        "category",
        "department",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [
        RoutineChecklistItemInline
    ]


# =====================================================
# CHECKLIST ITEMS
# =====================================================

@admin.register(RoutineChecklistItem)
class RoutineChecklistItemAdmin(
    admin.ModelAdmin
):

    list_display = (
        "routine",
        "sequence",
        "question",
        "response_type",
        "photo_required",
        "comment_required",
        "is_critical",
    )

    list_filter = (
        "response_type",
        "photo_required",
        "is_critical",
    )

    search_fields = (
        "question",
        "routine__routine_name",
    )


# =====================================================
# SCHEDULE
# =====================================================

@admin.register(RoutineSchedule)
class RoutineScheduleAdmin(
    admin.ModelAdmin
):

    list_display = (
        "routine",
        "frequency",
        "assigned_to",
        "reviewer",
        "approver",
        "start_date",
        "end_date",
        "is_active",
    )

    search_fields = (
        "routine__routine_name",
        "assigned_to__email",
    )

    list_filter = (
        "frequency",
        "is_active",
        "start_date",
    )

    date_hierarchy = "start_date"


# =====================================================
# EXECUTION
# =====================================================

@admin.register(RoutineExecution)
class RoutineExecutionAdmin(
    admin.ModelAdmin
):

    list_display = (
        "execution_no",
        "assigned_to",
        "due_date",
        "status",
        "completion_percentage",
        "created_at",
    )

    list_filter = (
        "status",
        "due_date",
        "created_at",
    )

    search_fields = (
        "execution_no",
        "assigned_to__email",
    )

    readonly_fields = (
        "created_at",
        "started_at",
        "submitted_at",
        "approved_at",
    )

    date_hierarchy = "created_at"

    inlines = [
        RoutineResponseInline,
        RoutineActivityInline,
    ]


# =====================================================
# RESPONSE
# =====================================================

@admin.register(RoutineResponse)
class RoutineResponseAdmin(
    admin.ModelAdmin
):

    list_display = (
        "execution",
        "checklist_item",
        "response",
        "submitted_by",
        "submitted_at",
    )

    list_filter = (
        "submitted_at",
    )

    search_fields = (
        "response",
        "comments",
        "checklist_item__question",
    )

    date_hierarchy = "submitted_at"


# =====================================================
# ATTACHMENTS
# =====================================================

@admin.register(RoutineAttachment)
class RoutineAttachmentAdmin(
    admin.ModelAdmin
):

    list_display = (
        "execution",
        "uploaded_by",
        "uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
    )


# =====================================================
# PHOTOS
# =====================================================

@admin.register(RoutinePhoto)
class RoutinePhotoAdmin(
    admin.ModelAdmin
):

    list_display = (
        "response",
        "uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
    )


# =====================================================
# ACTIVITY
# =====================================================

@admin.register(RoutineActivity)
class RoutineActivityAdmin(
    admin.ModelAdmin
):

    list_display = (
        "execution",
        "activity",
        "performed_by",
        "performed_at",
    )

    search_fields = (
        "activity",
        "remarks",
    )

    readonly_fields = (
        "performed_at",
    )


# =====================================================
# NCR
# =====================================================

@admin.register(RoutineNCR)
class RoutineNCRAdmin(
    admin.ModelAdmin
):

    list_display = (
        "ncr_no",
        "execution",
        "created_by",
        "created_at",
    )

    search_fields = (
        "ncr_no",
    )

    readonly_fields = (
        "created_at",
    )

    date_hierarchy = "created_at"
