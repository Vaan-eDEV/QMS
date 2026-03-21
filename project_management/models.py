from django.db import models
from django.conf import settings


class Project(models.Model):

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Stage(models.Model):

    name = models.CharField(max_length=100)
    sequence = models.IntegerField(default=1)

    def __str__(self):
        return self.name

import os
import uuid


def task_document_upload_path(instance, filename):

    ext = filename.split('.')[-1]

    new_filename = f"{uuid.uuid4()}.{ext}"

    project_name = instance.task.project.name.replace(" ", "_")

    task_name = instance.task.title.replace(" ", "_")

    return f"task_documents/{project_name}/{task_name}/{new_filename}"


class Task(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="assigned_tasks"
    )

    stage = models.ForeignKey(
        Stage,
        on_delete=models.SET_NULL,
        null=True
    )

    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        default='medium'
    )

    deadline = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    instruction = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.title
    

class TaskAttachment(models.Model):

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(
        upload_to=task_document_upload_path
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} - attachment"