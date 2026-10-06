from django.urls import path

from . import views

urlpatterns = [
    path("", views.my_tasks, name="my_tasks"),
    path("calendar/", views.calendar, name="calendar"),
    path("smart-selection/", views.smart_selection, name="smart_selection"),
    path("tasks/new/", views.task_create, name="task_create"),
    path("projects/new/", views.project_create, name="project_create"),
    path("tasks/<int:task_id>/edit/", views.task_edit, name="task_edit"),
    path("projects/<int:project_id>/edit/", views.project_edit, name="project_edit"),
    path("tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),
    path("tasks/<int:task_id>/status/", views.task_set_status, name="task_set_status"),
    path("projects/<int:project_id>/delete/", views.project_delete, name="project_delete"),
    path("projects/<int:project_id>/", views.project_board, name="project_board"),
    path("projects/<int:project_id>/list/", views.project_list, name="project_list"),
    path("projects/<int:project_id>/calendar/", views.project_calendar, name="project_calendar"),
]
