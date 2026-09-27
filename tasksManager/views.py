from django.shortcuts import render


def my_tasks(request):
    return render(request, "planner/my_tasks.html")


def calendar(request):
    return render(request, "planner/calendar.html")


def project_board(request, project_id):
    return render(request, "planner/project_board.html", {"project_id": project_id})


def project_list(request, project_id):
    return render(request, "planner/project_list.html", {"project_id": project_id})


def project_calendar(request, project_id):
    return render(request, "planner/project_calendar.html", {"project_id": project_id})
