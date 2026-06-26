from django.contrib import admin
from .models import (
    ChatChannel,
    ChatMessage,
    ChatAttachment,
    MessageRead,
    ChatNotification,
)


class ChatAttachmentInline(admin.TabularInline):
    model = ChatAttachment
    extra = 0


@admin.register(ChatChannel)
class ChatChannelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "channel_type",
        "created_by",
        "is_active",
        "created_at",
    )

    list_filter = (
        "channel_type",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    filter_horizontal = (
        "members",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "channel",
        "sender",
        "short_message",
        "created_at",
        "is_edited",
        "is_deleted",
    )

    list_filter = (
        "channel",
        "is_edited",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "message",
        "sender__username",
        "sender__first_name",
        "sender__last_name",
    )

    readonly_fields = (
        "created_at",
        "edited_at",
    )

    inlines = [ChatAttachmentInline]

    def short_message(self, obj):
        if obj.message:
            return obj.message[:50]
        return "-"
    short_message.short_description = "Message"


@admin.register(ChatAttachment)
class ChatAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "filename",
        "uploaded_at",
    )

    search_fields = (
        "file",
    )

    readonly_fields = (
        "uploaded_at",
    )

    def filename(self, obj):
        return obj.file.name.split("/")[-1]
    filename.short_description = "File Name"


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = (
        "message",
        "user",
        "read_at",
    )

    list_filter = (
        "read_at",
    )

    search_fields = (
        "user__username",
    )

    readonly_fields = (
        "read_at",
    )


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "message",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__username",
    )

    readonly_fields = (
        "created_at",
    )