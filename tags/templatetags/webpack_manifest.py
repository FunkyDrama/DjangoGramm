import json
from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings

register = template.Library()


@lru_cache(maxsize=1)
def _load_manifest():
    manifest_path = (
        Path(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0])
        / "dist"
        / "manifest.json"
    )
    try:
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


@register.simple_tag
def webpack_asset(name):
    manifest = _load_manifest()
    return manifest.get(name, name)
