from django.shortcuts import render, get_object_or_404, redirect
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Project, Stage, Task, TaskAttachment

# =================================================================================
# ============================= Project List ======================================
# =================================================================================
def project_list(request):

    projects = Project.objects.all()

    return render(
        request,
        "project/project_list.html",
        {"projects": projects}
    ) 

# =================================================================================
# ============================= Create Project ====================================
# =================================================================================
def project_create(request):

    if request.method == "POST":

        name = request.POST.get("name")
        description = request.POST.get("description")

        project = Project.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )

        return JsonResponse({
            "status": "success",
            "project_id": project.id
        })

    return JsonResponse({"status":"error"})

# -------------- Project delete -------------------
def project_delete(request, project_id):

    if request.method == "POST":

        try:
            project = Project.objects.get(id=project_id)

            project.delete()

            return JsonResponse({
                "status": "success"
            })

        except Project.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Project not found"
            })

    return JsonResponse({"status": "error"})

# =================================================================================
# ============================= Project Kanban ====================================
# =================================================================================
from django.contrib.auth import get_user_model
User = get_user_model()
def project_kanban(request, project_id):

    project = get_object_or_404(Project, id=project_id)

    stages = Stage.objects.all().order_by("sequence")

    tasks = Task.objects.filter(project=project)

    users = User.objects.all()

    return render(
        request,
        "project/kanban.html",
        {
            "project": project,
            "stages": stages,
            "tasks": tasks,
            "users": users
        }
    )

# =================================================================================
# ============================== Create Stage =====================================
# =================================================================================
def create_stage(request):

    if request.method == "POST":

        name = request.POST.get("name")

        stage = Stage.objects.create(
            name=name,
            sequence=Stage.objects.count() + 1
        )

        return JsonResponse({
            "status": "success",
            "stage_id": stage.id
        })

    return JsonResponse({"status": "error"}) 


# ------- Delete Stage -------
def delete_stage(request, stage_id):

    if request.method == "POST":

        try:
            stage = Stage.objects.get(id=stage_id)

            # Move tasks to another stage
            first_stage = Stage.objects.exclude(id=stage_id).first()

            if first_stage:
                Task.objects.filter(stage=stage).update(stage=first_stage)
            else:
                Task.objects.filter(stage=stage).update(stage=None)

            stage.delete()

            return JsonResponse({"status": "success"})

        except Stage.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Stage not found"})

    return JsonResponse({"status": "error"})

# =================================================================================
# ============================== Create Task ======================================
# =================================================================================
def create_task(request):

    if request.method == "POST":

        task = Task.objects.create(
            title=request.POST.get("title"),
            project_id=request.POST.get("project_id"),
            stage_id=request.POST.get("stage_id"),
            priority=request.POST.get("priority"),
            deadline=request.POST.get("deadline")
        )

        assigned_users = request.POST.getlist("assigned_to")

        if assigned_users:
            task.assigned_to.set(assigned_users)

        return JsonResponse({"status": "success"})

# --------------- Delete Task -----------------
def delete_task(request, task_id):

    if request.method == "POST":

        try:
            task = Task.objects.get(id=task_id)
            task.delete()

            return JsonResponse({"status": "success"})

        except Task.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Task not found"})

    return JsonResponse({"status": "error"})

# =================================================================================
# =============================== Task Detail =====================================
# =================================================================================
def task_detail(request, task_id):

    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":

        # Save instruction
        task.instruction = request.POST.get("instruction")
        task.save()

        # Handle multiple uploaded files
        files = request.FILES.getlist("documents")

        for f in files:
            TaskAttachment.objects.create(
                task=task,
                file=f,
                uploaded_by=request.user
            )

        return redirect("task_detail", task_id=task.id)

    attachments = task.attachments.all().order_by("-uploaded_at")

    return render(
        request,
        "project/task_detail.html",
        {
            "task": task,
            "attachments": attachments
        }
    )

# =================================================================================
# ============================= Update task Stage =================================
# =================================================================================
@csrf_exempt
def update_task_stage(request):

    if request.method == "POST":

        data = json.loads(request.body)

        task_id = data.get("task_id")
        stage_id = data.get("stage_id")

        try:
            task = Task.objects.get(id=task_id)

            task.stage_id = stage_id
            task.save()

            return JsonResponse({"status": "success"})

        except Task.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Task not found"})