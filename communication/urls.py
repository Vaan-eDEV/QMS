from django.urls import path
from . import views

urlpatterns = [

    # =======================
    # Communication Center
    # =======================

    path(
        "",
        views.communication_center,
        name="communication_center"
    ),

    # =======================
    # Channels
    # =======================

    path(
        "create-channel/",
        views.create_channel,
        name="create_channel"
    ),

    # =======================
    # Messages
    # =======================

    path(
        "send-message/<int:channel_id>/",
        views.send_message,
        name="send_message"
    ),

    path(
        "api/messages/<int:channel_id>/",
        views.get_messages,
        name="get_messages"
    ),

    path(
        "message/<int:message_id>/edit/",
        views.edit_message,
        name="edit_message"
    ),

    path(
        "message/<int:message_id>/delete/",
        views.delete_message,
        name="delete_message"
    ),
    path(
        "api/users/",
        views.get_users,
        name="get_users"
    ),

    path(
        "chat-notifications/",
        views.chat_notifications,
        name="chat_notifications"
    )
]