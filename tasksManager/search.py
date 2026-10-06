import re
from datetime import timedelta
from difflib import SequenceMatcher

from django.utils import timezone

from tasksManager.models import Project, Task

# слова-подсказки превращаются в фильтры, остальное ищется по тексту
STATUS_WORDS = {
    "active": "active", "активные": "active", "активная": "active", "работе": "active", "работа": "active",
    "complete": "complete", "done": "complete", "готово": "complete", "готовые": "complete", "готовая": "complete",
    "created": "created", "создана": "created", "новые": "created",
    "inactive": "inactive", "пауза": "inactive", "паузе": "inactive",
}
PRIORITY_WORDS = {
    "high": "high", "высокий": "high", "срочно": "high",
    "medium": "medium", "средний": "medium",
    "low": "low", "низкий": "low",
}
OVERDUE_WORDS = {"просрочено", "просроченные", "overdue", "expired"}
TODAY_WORDS = {"сегодня", "today"}


def normalize(text):
    return re.sub(r"\s+", " ", (text or "").lower().replace("ё", "е")).strip()


def words(text):
    return re.findall(r"\w+", normalize(text))


def word_score(token, text_words):
    """1.0 — слово совпало целиком, 0.8 — по началу, 0.5 — опечатка; 0 — не нашлось."""
    best = 0.0
    for w in text_words:
        if w == token:
            return 1.0
        if len(token) >= 3 and w.startswith(token):
            best = max(best, 0.8)
        elif len(token) >= 4 and len(w) >= 4 and SequenceMatcher(None, token, w).ratio() >= 0.8:
            best = max(best, 0.5)
    return best


def search_tasks(query, limit=50):
    """Умный подбор: все слова запроса должны найтись (в названии, описании, проекте или у исполнителей),
    учитываются окончания и опечатки; «просрочено», «сегодня», «в работе», «high» работают как фильтры."""
    today = timezone.localdate()
    tokens, statuses, priorities, overdue, due_today = [], set(), set(), False, False
    for t in words(query):
        if t in STATUS_WORDS:
            statuses.add(STATUS_WORDS[t])
        elif t in PRIORITY_WORDS:
            priorities.add(PRIORITY_WORDS[t])
        elif t in OVERDUE_WORDS:
            overdue = True
        elif t in TODAY_WORDS:
            due_today = True
        elif t not in {"в", "на", "по", "и", "the", "in"}:
            tokens.append(t)

    tasks = Task.objects.select_related("project").prefetch_related("workers")
    if statuses:
        tasks = tasks.filter(status__in=statuses)
    if priorities:
        tasks = tasks.filter(priority__in=priorities)
    if overdue:
        tasks = tasks.filter(end_date__lt=today).exclude(status="complete")
    if due_today:
        tasks = tasks.filter(end_date=today)

    scored = []
    for task in tasks:
        fields = [
            (3.0, words(task.title)),
            (2.0, words(task.project.title)),
            (2.0, words(" ".join(w.get_full_name() or w.username for w in task.workers.all()))),
            (1.0, words(task.description)),
        ]
        total = 0.0
        for token in tokens:
            hit = max((weight * word_score(token, fw) for weight, fw in fields), default=0)
            if not hit:
                total = 0
                break
            total += hit
        if tokens and not total:
            continue
        scored.append((total, task))

    scored.sort(key=lambda p: (-p[0], p[1].end_date))
    return [t for _, t in scored[:limit]], bool(tokens or statuses or priorities or overdue or due_today)


def search_projects(query):
    tokens = words(query)
    if not tokens:
        return []
    return [p for p in Project.objects.all()
            if all(word_score(t, words(p.title)) for t in tokens)]
