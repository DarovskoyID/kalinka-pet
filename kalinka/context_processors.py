from pathlib import Path

from django.conf import settings

STATIC_DIR = Path(settings.BASE_DIR) / "static"


def static_version(request):
    """Версия статики для ссылок вида {% static 'x.css' %}?v={{ static_version }}:
    меняется при любом изменении файлов, поэтому браузер не держит старые CSS/JS."""
    try:
        version = int(max(p.stat().st_mtime for p in STATIC_DIR.rglob("*") if p.is_file()))
    except ValueError:  # пустая папка
        version = 0
    return {"static_version": version}
