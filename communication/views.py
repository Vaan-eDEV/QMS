from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import *
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def create_channel(request):

    if request.method == "POST":

        name = request.POST.get("name")
        description = request.POST.get("description")
        channel_type = request.POST.get(
            "channel_type",
            "public"
        )

        selected_users = request.POST.getlist(
            "members"
        )

        channel = ChatChannel.objects.create(
            name=name,
            description=description,
            channel_type=channel_type,
            created_by=request.user,
        )

        if channel_type == "public":

            channel.members.set(
                User.objects.all()
            )

        else:

            channel.members.add(request.user)

            if selected_users:
                channel.members.add(
                    *User.objects.filter(
                        id__in=selected_users
                    )
                )

        messages.success(
            request,
            "Channel created successfully."
        )

        return redirect(
            reverse("communication_center")
            + f"?channel={channel.id}"
        )

    users = User.objects.filter(
        is_active=True
    ).order_by(
        "first_name"
    )

    context = {
        "users": users
    }

    return render(
        request,
        "communication/create_channel.html",
        context
    )


# @login_required
# def channel_list(request):

#     if request.user.is_superuser:
#         channels = ChatChannel.objects.filter(
#             is_active=True
#         )
#     else:
#         channels = ChatChannel.objects.filter(
#             members=request.user,
#             is_active=True
#         ).distinct()

#     context = {
#         "channels": channels,
#     }

#     return render(
#         request,
#         "communication/channel_list.html",
#         context,
#     )


# @login_required
# def chat_room(request, channel_id):

#     channel = get_object_or_404(
#         ChatChannel,
#         id=channel_id,
#         is_active=True
#     )

#     if not request.user.is_superuser:
#         if request.user not in channel.members.all():
#             messages.error(
#                 request,
#                 "You are not authorized to access this channel."
#             )
#             return redirect("channel_list")

#     chat_messages = (
#         ChatMessage.objects
#         .filter(channel=channel)
#         .select_related("sender")
#         .prefetch_related("attachments")
#         .order_by("created_at")
#     )

#     context = {
#         "channel": channel,
#         "chat_messages": chat_messages,
#     }

#     return render(
#         request,
#         "communication/chat_room.html",
#         context,
#     )

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import re

@login_required
def send_message(request, channel_id):

    if request.method != "POST":

        return redirect(
            reverse("communication_center")
            + f"?channel={channel_id}"
        )

    channel = get_object_or_404(
        ChatChannel,
        id=channel_id,
        is_active=True
    )

    # Permission Check
    if (
        not request.user.is_superuser
        and request.user not in channel.members.all()
    ):

        messages.error(
            request,
            "You are not authorized to send messages in this channel."
        )

        return redirect(
            "communication_center"
        )

    message_text = request.POST.get(
        "message",
        ""
    ).strip()

    uploaded_files = request.FILES.getlist(
        "attachments"
    )

    # Prevent Empty Messages
    if not message_text and not uploaded_files:

        return redirect(
            reverse("communication_center")
            + f"?channel={channel.id}"
        )

    # Create Message
    chat_message = ChatMessage.objects.create(

        channel=channel,

        sender=request.user,

        message=message_text,

    )

    # Save Attachments
    for file in uploaded_files:

        ChatAttachment.objects.create(

            message=chat_message,

            file=file,

        )

    # ==================================
    # NOTIFY ALL CHANNEL MEMBERS
    # ==================================

    members = channel.members.exclude(
        id=request.user.id
    )

    for member in members:

        ChatNotification.objects.create(

            user=member,

            message=chat_message

        )

    # ==================================
    # EXTRA NOTIFICATION FOR @MENTIONS
    # ==================================

    mentions = re.findall(
        r'@([A-Za-z0-9_]+)',
        message_text
    )

    for mention in mentions:

        mentioned_user = User.objects.filter(
            first_name__iexact=mention
        ).first()

        if (
            mentioned_user
            and mentioned_user != request.user
        ):

            already_exists = ChatNotification.objects.filter(
                user=mentioned_user,
                message=chat_message
            ).exists()

            if not already_exists:

                ChatNotification.objects.create(

                    user=mentioned_user,

                    message=chat_message

                )

    return redirect(

        reverse("communication_center")
        + f"?channel={channel.id}"

    )



@login_required
def get_users(request):

    users = User.objects.filter(is_active=True)

    data = []

    for u in users:
        data.append({
            "id": u.id,
            "name": u.get_display_name()
        })

    return JsonResponse({
        "users": data
    }) 



@login_required
def communication_center(request):

    if request.user.is_superuser:

        channels = ChatChannel.objects.filter(
            is_active=True
        )

    else:

        channels = (
            ChatChannel.objects
            .filter(
                members=request.user,
                is_active=True
            )
            .distinct()
        )

    selected_channel_id = request.GET.get(
        "channel"
    )

    selected_channel = None

    chat_messages = ChatMessage.objects.none()

    # Auto-select first channel
    if not selected_channel_id and channels.exists():

        selected_channel = channels.first()

        # MARK NOTIFICATIONS AS READ
        ChatNotification.objects.filter(
            user=request.user,
            message__channel=selected_channel,
            is_read=False
        ).update(
            is_read=True
        )

        chat_messages = (
            ChatMessage.objects
            .filter(channel=selected_channel)
            .select_related("sender")
            .prefetch_related("attachments")
            .order_by("created_at")
        )

    # Selected channel
    elif selected_channel_id:

        selected_channel = get_object_or_404(
            ChatChannel,
            id=selected_channel_id,
            is_active=True
        )

        if (
            not request.user.is_superuser
            and request.user
            not in selected_channel.members.all()
        ):

            messages.error(
                request,
                "You are not authorized to access this channel."
            )

            return redirect(
                "communication_center"
            )

        # MARK NOTIFICATIONS AS READ
        ChatNotification.objects.filter(
            user=request.user,
            message__channel=selected_channel,
            is_read=False
        ).update(
            is_read=True
        )

        chat_messages = (
            ChatMessage.objects
            .filter(channel=selected_channel)
            .select_related("sender")
            .prefetch_related("attachments")
            .order_by("created_at")
        )

    # Online Users
    online_users = (
        User.objects
        .filter(is_active=True)
        .order_by("first_name")
    )

    # Users for Create Channel Modal
    users = (
        User.objects
        .filter(is_active=True)
        .exclude(id=request.user.id)
        .order_by("first_name")
    )

    context = {

        "channels": channels,

        "selected_channel":
        selected_channel,

        "chat_messages":
        chat_messages,

        "online_users":
        online_users,

        "users":
        users,

    }

    return render(
        request,
        "communication/chat_center.html",
        context
    )




@login_required
def edit_message(request, message_id):

    message = get_object_or_404(
        ChatMessage,
        id=message_id,
        sender=request.user
    )

    if request.method == "POST":

        message.message = request.POST.get(
            "message"
        )

        message.is_edited = True

        message.edited_at = timezone.now()

        message.save()

        return JsonResponse({
            "success": True
        })

    return JsonResponse({
        "success": False
    })




@login_required
def delete_message(request, message_id):

    message = get_object_or_404(
        ChatMessage,
        id=message_id,
        sender=request.user
    )

    message.is_deleted = True

    message.message = "Message deleted"

    message.save()

    return JsonResponse({
        "success": True
    })







from django.http import JsonResponse

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required
def get_messages(request, channel_id):

    channel = get_object_or_404(
        ChatChannel,
        id=channel_id,
        is_active=True
    )

    if (
        not request.user.is_superuser
        and request.user not in channel.members.all()
    ):
        return JsonResponse(
            {"error": "Unauthorized"},
            status=403
        )

    data = []

    chat_messages = (
        ChatMessage.objects
        .filter(
            channel=channel
        )
        .select_related(
            "sender"
        )
        .prefetch_related(
            "attachments"
        )
        .order_by(
            "created_at"
        )
    )

    for msg in chat_messages:

        attachments = []

        for attachment in msg.attachments.all():

            attachments.append({

                "filename":
                attachment.filename,

                "url":
                attachment.file.url
                if attachment.file
                else "",

            })

        data.append({

            "id":
            msg.id,

            "sender":
            msg.sender.get_display_name(),

            "sender_id":
            msg.sender.id,

            "message":
            "Message deleted"
            if msg.is_deleted
            else (msg.message or ""),

            "time":
            timezone.localtime(
                msg.created_at
            ).strftime(
                "%d %b %Y %I:%M %p"
            ),

            "mine":
            msg.sender_id ==
            request.user.id,

            "is_edited":
            msg.is_edited,

            "edited_at":
            timezone.localtime(
                msg.edited_at
            ).strftime(
                "%d %b %Y %I:%M %p"
            ) if msg.edited_at else "",

            "is_deleted":
            msg.is_deleted,

            "attachments":
            attachments,

            "has_mention":
            "@" in (msg.message or ""),

        })

    return JsonResponse({

        "messages": data

    })

@login_required
def chat_notifications(request):

    notifications = (
        ChatNotification.objects
        .filter(
            user=request.user,
            is_read=False
        )
        .select_related(
            "message",
            "message__sender"
        )
        .order_by("-created_at")
    )

    data = []

    for n in notifications:

        data.append({

            "id": n.id,

            "sender":
            n.message.sender.get_display_name(),

            "message":
            n.message.message,

            "channel_id":
            n.message.channel.id,

        })

    return JsonResponse({
        "notifications": data
    })