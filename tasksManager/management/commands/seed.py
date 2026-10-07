import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from tasksManager.models import Project, Task, statuses, priorities

User = get_user_model()

WORDS = ["Api", "Backend", "Frontend", "Дизайн", "Отчёт", "Тесты", "Деплой", "База данных",
         "Авторизация", "Календарь", "Поиск", "Уведомления", "Рефакторинг", "Баг", "Интеграция"]
VERBS = ["Сделать", "Исправить", "Проверить", "Обновить", "Добавить", "Удалить", "Настроить"]


class Command(BaseCommand):
    help = "Заполняет базу тестовыми юзерами, проектами и тасками"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=340)
        parser.add_argument("--projects", type=int, default=55)
        parser.add_argument("--tasks", type=int, default=5000)
        parser.add_argument("--seed", type=int, default=None, help="для повторяемого результата")

    @transaction.atomic
    def handle(self, *args, **o):
        rnd = random.Random(o["seed"])
        password = make_password("test12345")  # один хеш на всех, иначе 340 хешей очень долго
        start_id = User.objects.count()

        users = User.objects.bulk_create([
            User(username=f"seed_user_{start_id + i}", email=f"seed{start_id + i}@example.com",
                 password=password, telegram_id=str(rnd.randint(10**8, 10**9)),
                 github_url=f"https://github.com/seed{start_id + i}", bio="Тестовый пользователь")
            for i in range(o["users"])
        ])
        users = list(User.objects.filter(username__startswith="seed_user_").order_by("-id")[:o["users"]])

        projects = Project.objects.bulk_create([
            Project(title=f"Проект {i + 1}: {rnd.choice(WORDS)}",
                    color_Red=rnd.randint(0, 255), color_Green=rnd.randint(0, 255), color_Blue=rnd.randint(0, 255))
            for i in range(o["projects"])
        ])
        projects = list(Project.objects.order_by("-id")[:o["projects"]])

        today = date.today()
        tasks = []
        for i in range(o["tasks"]):
            start = today + timedelta(days=rnd.randint(-60, 30))
            end = start + timedelta(days=rnd.randint(1, 30))
            status = rnd.choice(list(statuses))
            tasks.append(Task(
                title=f"{rnd.choice(VERBS)} {rnd.choice(WORDS)} #{i + 1}",
                description="Тестовое описание задачи",
                start_date=start, end_date=end,
                completed=min(end, today) if status == "complete" else None,
                status=status, priority=rnd.choice(list(priorities)),
                project=rnd.choice(projects),
            ))
        Task.objects.bulk_create(tasks)
        created = list(Task.objects.order_by("-id")[:o["tasks"]])

        Through = Task.workers.through
        Through.objects.bulk_create([
            Through(task_id=t.id, user_id=u.id)
            for t in created
            for u in rnd.sample(users, rnd.randint(1, 4))
        ], batch_size=2000)

        self.stdout.write(self.style.SUCCESS(
            f"Создано: {len(users)} юзеров, {len(projects)} проектов, {len(created)} тасок"))
