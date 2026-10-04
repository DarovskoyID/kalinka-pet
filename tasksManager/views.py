from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from tasksManager.forms import ProjectForm, TaskForm
from tasksManager.models import Project, Task
from tasksManager.models import statuses



@login_required
def my_tasks(request):
    model = Task
    today = timezone.localtime()

    count_projects = model.objects.filter(workers=request.user).values("project").distinct().count()

    week_start = (today - timedelta(days=today.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    count_completed_tasks_for_the_week = model.objects.filter(
        status="complete",
        completed__gte=week_start,
    ).count()

    today_must_be_completed = model.objects.filter(end_date=today)
    count_today_must_be_completed = today_must_be_completed.count()
    today_must_be_completed = (
        today_must_be_completed
        .exclude()
        .select_related("project")
        .prefetch_related("workers")
        .order_by("end_date")
    )

    expired_tasks = model.objects.filter(end_date__lt=today).exclude(status="complete")
    count_expired_tasks = expired_tasks.count()
    expired_tasks = (
        expired_tasks
        .exclude(status="complete")
        .select_related("project")
        .prefetch_related("workers")
        .order_by("end_date")
    )

    in_work = model.objects.filter(status="active")
    count_in_work = in_work.count()

    context = {
        "count_expired_tasks" : count_expired_tasks,
        "count_today_must_be_completed" : count_today_must_be_completed,
        "count_in_work" : count_in_work,
        "count_completed_tasks_for_the_week" : count_completed_tasks_for_the_week,
        "expired_tasks" : expired_tasks,
        "in_work" : in_work,
        "today_must_be_completed" : today_must_be_completed,
        "count_projects" : count_projects,
    }
    return render(request, "planner/my_tasks.html", context)

@login_required
def calendar(request):
    return render(request, "planner/calendar.html")

@login_required
def project_board(request, project_id):
    model = Task
    today = timezone.localtime()

    in_work = model.objects.filter(status="active", project_id=project_id)
    count_in_work = in_work.count()

    completed_tasks = model.objects.filter(status="complete", project_id=project_id)
    count_completed_tasks = completed_tasks.count()

    queued_tasks = model.objects.filter(status__in=["inactive", "created"], project_id=project_id)
    count_queued_tasks = queued_tasks.count()

    context = {
        "count_in_work": count_in_work,
        "in_work": in_work,
        "count_completed_tasks": count_completed_tasks,
        "completed_tasks": completed_tasks,
        "count_queued_tasks": count_queued_tasks,
        "queued_tasks": queued_tasks,
    }
    return render(request, "planner/project_board.html", context)

@login_required
def project_list(request, project_id):
    return render(request, "planner/project_list.html", {"project_id": project_id})

@login_required
def project_calendar(request, project_id):
    return render(request, "planner/project_calendar.html", {"project_id": project_id})

@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            next_url = request.POST.get("next")
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect("my_tasks")
    else:
        form = TaskForm(initial={"workers": [request.user.pk], "start_date": timezone.localdate()})

    return render(request, "planner/task_create.html", {"task_form": form})

@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect("project_board", project_id=project.id)
    else:
        form = ProjectForm()

    return render(request, "planner/project_create.html", {"project_form": form})

def _safe_next(request, fallback):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return fallback

@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    next_url = _safe_next(request, reverse("project_board", args=[task.project_id]))
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(next_url)
    else:
        form = TaskForm(instance=task)

    # не "task_form": так называется форма создания в модалке base_app
    return render(request, "planner/task_edit.html", {"edit_form": form, "task": task, "next": next_url})

@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project_board", project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, "planner/project_edit.html", {"edit_form": form})

@login_required
@require_POST
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    next_url = _safe_next(request, reverse("project_board", args=[task.project_id]))
    task.delete()
    return redirect(next_url)

@login_required
@require_POST
def project_delete(request, project_id):
    # задачи проекта удалятся каскадом (on_delete=CASCADE)
    get_object_or_404(Project, pk=project_id).delete()
    return redirect("my_tasks")
