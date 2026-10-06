from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from tasksManager.forms import STATUS_CHOICES, ProjectForm, TaskForm
from tasksManager.models import Project, Task
from tasksManager.models import statuses
from tasksManager.search import search_projects, search_tasks



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

MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]


def _calendar_context(request, tasks):
    """Сетка месяца (6 недель, с понедельника) с задачами по сроку; месяц берётся из ?month=YYYY-MM."""
    today = timezone.localdate()
    try:
        year, month = map(int, request.GET.get("month", "").split("-"))
        first = date(year, month, 1)
    except ValueError:
        first = today.replace(day=1)

    start = first - timedelta(days=first.weekday())
    end = start + timedelta(days=41)
    by_day = {}
    for task in tasks.filter(end_date__range=(start, end)).select_related("project"):
        by_day.setdefault(task.end_date, []).append(task)

    days = [start + timedelta(days=i) for i in range(42)]
    prev_month = (first - timedelta(days=1)).replace(day=1)
    next_month = (first + timedelta(days=32)).replace(day=1)
    return {
        "cal_title": f"{MONTHS[first.month - 1]} {first.year}",
        "cal_prev": prev_month.strftime("%Y-%m"),
        "cal_next": next_month.strftime("%Y-%m"),
        "cal_days": [
            {"date": d, "other": d.month != first.month, "today": d == today, "tasks": by_day.get(d, [])}
            for d in days
        ],
    }

@login_required
def calendar(request):
    # общий календарь: задачи всех проектов
    return render(request, "planner/calendar.html", _calendar_context(request, Task.objects.all()))

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
    tasks = (
        Task.objects.filter(project_id=project_id)
        .prefetch_related("workers")
        .order_by("end_date", "id")
    )
    return render(request, "planner/project_list.html", {"tasks": tasks, "today": timezone.localdate()})

@login_required
def project_calendar(request, project_id):
    tasks = Task.objects.filter(project_id=project_id)
    return render(request, "planner/project_calendar.html", _calendar_context(request, tasks))

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

@login_required
@require_POST
def task_set_status(request, task_id):
    """Смена статуса перетаскиванием карточки на доске (fetch из static/js/app.js)."""
    task = get_object_or_404(Task, pk=task_id)
    status = request.POST.get("status")
    if status not in dict(STATUS_CHOICES):
        return JsonResponse({"error": "Неизвестный статус"}, status=400)

    task.status = status
    # дата закрытия нужна для счётчика «Закрыто за неделю»
    task.completed = (task.completed or timezone.localdate()) if status == "complete" else None
    task.save(update_fields=["status", "completed"])
    return JsonResponse({"id": task.id, "status": task.status})

@login_required
def knowledge_search(request):
    query = request.GET.get("q", "").strip()
    tasks, _ = search_tasks(query) if query else ([], False)
    context = {
        "q": query,
        "tasks": tasks,
        "projects": search_projects(query) if query else [],
        "today": timezone.localdate(),
    }
    return render(request, "planner/knowledge_search.html", context)
