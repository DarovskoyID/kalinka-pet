from django.urls import path

from . import views

urlpatterns = [
    path("", views.my_tasks, name="my_tasks"),
    path("calendar/", views.calendar, name="calendar"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("projects/new/", views.project_create, name="project_create"),
    path("projects/<int:project_id>/", views.project_board, name="project_board"),
    path("projects/<int:project_id>/list/", views.project_list, name="project_list"),
    path("projects/<int:project_id>/calendar/", views.project_calendar, name="project_calendar"),
]
