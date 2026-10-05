from django import template
from django.utils.html import format_html

register = template.Library()

# цвета из static/css/base.css; один и тот же пользователь всегда получает один цвет
PALETTE = ["green", "violet", "sky", "amber", "red"]


def initials(user):
    """Первые буквы имени и фамилии; если имени нет — первая буква логина."""
    letters = "".join(part[:1] for part in (user.first_name.strip(), user.last_name.strip()) if part)
    return (letters or user.username[:1]).upper()


@register.filter(name="initials")
def initials_filter(user):
    return initials(user)


@register.simple_tag
def avatar(user, size=""):
    css = "avatar" + (f" avatar--{size}" if size else "")
    name = user.get_full_name() or user.username
    return format_html(
        '<span class="{}" style="--a: var(--{})" title="{}">{}</span>',
        css, PALETTE[user.pk % len(PALETTE)], name, initials(user),
    )
