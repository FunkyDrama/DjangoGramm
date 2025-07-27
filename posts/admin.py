from django.contrib import admin

from posts.models import Post


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
