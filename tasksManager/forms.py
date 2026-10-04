from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from tasksManager.models import Project, Task

# В моделях статусы/приоритеты заданы как {"ключ": число}, поэтому
# человекочитаемые подписи для селектов задаём здесь.
STATUS_CHOICES = [
    ("created", "Создана"),
    ("active", "В работе"),
    ("inactive", "На паузе"),
    ("complete", "Готово"),
]

PRIORITY_CHOICES = [
    ("low", "Низкий"),
    ("medium", "Средний"),
    ("high", "Высокий"),
]


class WorkerChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, user):
        return user.get_full_name() or user.username


class TaskForm(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUS_CHOICES, initial="created",
                               widget=forms.Select(attrs={"class": "input"}))
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, initial="medium",
                                 widget=forms.RadioSelect)
    workers = WorkerChoiceField(queryset=get_user_model().objects.all(),
                                widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Task
        fields = ["title", "description", "project", "status", "priority",
                  "start_date", "end_date", "workers"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "modal-title-input", "placeholder": "Что нужно сделать?"}),
            "description": forms.Textarea(attrs={"class": "input", "rows": 3, "placeholder": "Описание, ссылки, детали…"}),
            "project": forms.Select(attrs={"class": "input"}),
            "start_date": forms.DateInput(attrs={"class": "input", "type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"class": "input", "type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.order_by("title")
        self.fields["project"].empty_label = None

    def clean(self):
        cleaned_data = super().clean()
        start, end = cleaned_data.get("start_date"), cleaned_data.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "Срок не может быть раньше начала")
        return cleaned_data

    def save(self, commit=True):
        task = super().save(commit=False)
        # дата закрытия нужна для счётчика «Закрыто за неделю»
        if task.status == "complete":
            task.completed = task.completed or timezone.localdate()
        else:
            task.completed = None
        if commit:
            task.save()
            self.save_m2m()
        return task


PROJECT_COLORS = ["#3ecf8e", "#5cc8f2", "#f2c14e", "#a78bfa", "#f26d6d", "#f28fc4"]


class ProjectForm(forms.ModelForm):
    # В модели цвет хранится тремя полями RGB, в форме — одной hex-строкой
    color = forms.RegexField(regex=r"^#[0-9a-fA-F]{6}$", initial=PROJECT_COLORS[0],
                             error_messages={"invalid": "Цвет должен быть в формате #RRGGBB"})

    class Meta:
        model = Project
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input", "placeholder": "Например, «Ремонт»", "autocomplete": "off"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            p = self.instance
            self.initial["color"] = f"#{p.color_Red:02x}{p.color_Green:02x}{p.color_Blue:02x}"

    def save(self, commit=True):
        project = super().save(commit=False)
        h = self.cleaned_data["color"].lstrip("#")
        project.color_Red, project.color_Green, project.color_Blue = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        if commit:
            project.save()
        return project
