import re
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()
HASHTAG_RE = re.compile(r"#(?P<tag>[\w\d_]+)")


@register.filter
def hashtagify(text):
    def repl(m):
        raw = m.group("tag")
        slug = raw.lower()
        url = reverse("tagged_posts", kwargs={"slug": slug})
        return (
            f'<a href="{url}" '
            f'class="text-blue-500 hover:text-blue-800 transition-colors duration-150 font-medium no-underline hover:underline">'
            f"#{raw}</a>"
        )

    return mark_safe(HASHTAG_RE.sub(repl, text))
