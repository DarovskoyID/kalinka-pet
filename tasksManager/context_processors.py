from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from tasksManager.forms import PROJECT_COLORS, ProjectForm, TaskForm
from tasksManager.models import Project


PLANNER_PAGES = {"my_tasks", "calendar", "smart_selection", "project_board", "project_list", "project_calendar", "task_create",
                 "project_create", "task_edit", "project_edit"}


def week_progress(user):
    """Прогресс недели (пн-вс) по задачам пользователя: done — закрыто на этой неделе,
    total — закрытые + ещё открытые со сроком на этой неделе. Тот же done показывает плитка «Закрыто за неделю»."""
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week = (week_start, week_start + timedelta(days=6))
    done = user.tasks.filter(status="complete", completed__range=week).count()
    still_open = user.tasks.filter(end_date__range=week).exclude(status="complete").count()
    total = done + still_open
    return {"total": total, "done": done, "percent": round(done * 100 / total) if total else 0}


def planner(request):
    match = request.resolver_match
    if not request.user.is_authenticated or not match or match.url_name not in PLANNER_PAGES:
        return {}

    user = request.user
    project_id = match.kwargs.get("project_id")
    current_project = get_object_or_404(Project, pk=project_id) if project_id else None
    today = timezone.localdate()
    week = week_progress(user)

    initial = {"workers": [user.pk], "start_date": today}
    if project_id:
        initial["project"] = project_id

    return {
        "project_id": project_id,
        "project_members": get_user_model().objects.filter(tasks__project_id=project_id).distinct().order_by("first_name", "username") if project_id else [],
        "current_project": current_project,
        "sidebar_projects": Project.objects.annotate(task_count=Count("task")).order_by("title"),
        "my_open_tasks_count": user.tasks.exclude(status="complete").count(),
        "week_total": week["total"],
        "week_done": week["done"],
        "week_percent": week["percent"],
        "task_form": TaskForm(initial=initial),
        "project_form": ProjectForm(),
        "project_colors": PROJECT_COLORS,
    }
