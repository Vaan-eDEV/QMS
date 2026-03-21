from django.contrib import admin
from .models import Project, Task, Stage, TaskAttachment

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Stage)
admin.site.register(TaskAttachment)