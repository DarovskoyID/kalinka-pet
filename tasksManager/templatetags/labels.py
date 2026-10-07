from django import template

register = template.Library()

# Подписи только для отображения: в БД и в models.py остаются ключи (complete, high, ...)
STATUS_LABELS = {
    "created": "Создана",
    "active": "В работе",
    "inactive": "Приостановлена",
    "complete": "Выполнена",
}

PRIORITY_LABELS = {
    "low": "Низкий",
    "medium": "Средний",
    "high": "Высокий",
}


@register.filter
def status_label(value):
    return STATUS_LABELS.get(value, value)


@register.filter
def priority_label(value):
    return PRIORITY_LABELS.get(value, value)
