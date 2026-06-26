from django.db import models
from django.conf import settings


class ChatChannel(models.Model):
    """
    Channel / Group
    Example:
    - General
    - Quality
    - Production
    - Audit
    """

    CHANNEL_TYPES = [
        ("public", "Public"),
        ("private", "Private"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    channel_type = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPES,
        default="public"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_channels"
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="chat_channels"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    """
    Text message sent to channel
    """

    channel = models.ForeignKey(
        ChatChannel,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    message = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    edited_at = models.DateTimeField(
        blank=True,
        null=True
    )

    is_edited = models.BooleanField(
        default=False
    )

    is_deleted = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender} - {self.channel}"


class ChatAttachment(models.Model):
    """
    Files attached to a message
    Supports:
    - PDF
    - DOCX
    - XLSX
    - JPG
    - PNG
    """

    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(
        upload_to="chat_uploads/%Y/%m/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )
    @property
    def filename(self):
        return self.file.name.split("/")[-1]
    @property
    def is_image(self):

        image_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
        ]

        return self.file.name.lower().endswith(
            tuple(image_extensions)
        )
    def __str__(self):
        return self.filename()


class MessageRead(models.Model):
    """
    Read receipt
    """

    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="reads"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    read_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("message", "user")

    def __str__(self):
        return f"{self.user} read {self.message.id}"


class ChatNotification(models.Model):
    """
    Notification for unread messages
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_notifications"
    )

    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - Notification"