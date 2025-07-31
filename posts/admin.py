from django.contrib import admin

from posts.models import Post
from tags.models import Tag


class TagInline(admin.TabularInline):
    model = Tag.posts.through
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "caption")
    list_filter = ("author", "created")
    search_fields = (
        "caption",
        "author__user__username",
    )
    date_hierarchy = "created"
    ordering = ("-created",)
    inlines = (TagInline,)
    exclude = ("tags",)
