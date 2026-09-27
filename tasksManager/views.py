from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from tasksManager.forms import TaskForm
from tasksManager.models import Task
from tasksManager.models import statuses



@login_required
def my_tasks(request):
    model = Task;
    today = timezone.localtime()

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

    expired_tasks = model.objects.filter(end_date__lt=today)
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
        "today_must_be_completed" : today_must_be_completed
    }
    return render(request, "planner/my_tasks.html", context)

@login_required
def calendar(request):
    return render(request, "planner/calendar.html")

@login_required
def project_board(request, project_id):
    return render(request, "planner/project_board.html", {"project_id": project_id})

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
